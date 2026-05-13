"""Move nested Case Session Attachment rows into additional_attachments (one URL per line)."""

from __future__ import annotations

import frappe


def _merge_urls(existing: str | None, new_urls: list[str]) -> str:
	lines = [line.strip() for line in (existing or "").splitlines() if line.strip()]
	seen = set(lines)
	for url in new_urls:
		url = (url or "").strip()
		if url and url not in seen:
			lines.append(url)
			seen.add(url)
	return "\n".join(lines)


def execute():
	if not frappe.db.table_exists("tabCase Session Attachment"):
		return

	rows = frappe.db.sql(
		"""
		select parent, parenttype, `file`
		from `tabCase Session Attachment`
		where ifnull(`file`, '') != ''
		order by idx, creation
		""",
		as_dict=True,
	)

	by_parent: dict[tuple[str, str], list[str]] = {}
	for row in rows:
		key = (row.parenttype, row.parent)
		by_parent.setdefault(key, []).append(row.file)

	for (parenttype, parent), urls in by_parent.items():
		if not parenttype or not parent or not urls:
			continue
		existing = frappe.db.get_value(parenttype, parent, "additional_attachments")
		merged = _merge_urls(existing, urls)
		if merged != (existing or ""):
			frappe.db.set_value(parenttype, parent, "additional_attachments", merged, update_modified=False)

	frappe.db.sql("delete from `tabCase Session Attachment`")
	frappe.db.commit()
