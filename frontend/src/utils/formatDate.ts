/**
 * Centralized Date & Time Formatting Utility for AI SOC Monitoring Platform
 * 
 * Canonical Architecture:
 * Backend / DB / API = UTC ISO-8601 (e.g. "2026-08-12T16:10:00Z")
 * Frontend Display = Local Timezone aware parsing (Asia/Kolkata IST = UTC+05:30)
 * Format Example: "12 Aug 2026, 21:40:00 IST"
 */
export function formatTimestamp(
  dateInput?: string | Date | number | null,
  timeZone: string = 'Asia/Kolkata'
): string {
  if (!dateInput) return 'N/A';
  try {
    const d = typeof dateInput === 'string' || typeof dateInput === 'number' ? new Date(dateInput) : dateInput;
    if (isNaN(d.getTime())) return String(dateInput);

    const formatter = new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false,
      timeZone: timeZone,
    });

    const parts = formatter.formatToParts(d);
    const partMap: Record<string, string> = {};
    for (const p of parts) {
      partMap[p.type] = p.value;
    }

    const tzLabel = timeZone === 'Asia/Kolkata' ? 'IST' : 'UTC';
    return `${partMap.day} ${partMap.month} ${partMap.year}, ${partMap.hour}:${partMap.minute}:${partMap.second} ${tzLabel}`;
  } catch {
    return String(dateInput);
  }
}
