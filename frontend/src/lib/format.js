/**
 * Formats currency amount using INR en-IN locale by default
 */
export function formatMoney(amount, currency = 'INR') {
  if (amount === null || amount === undefined || isNaN(amount)) {
    return '—';
  }
  try {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: currency || 'INR',
      maximumFractionDigits: 2,
    }).format(amount);
  } catch (e) {
    return `${currency || '₹'} ${Number(amount).toFixed(2)}`;
  }
}

/**
 * Formats ISO date string (YYYY-MM-DD) to 'DD MMM YYYY'
 */
export function formatDate(dateString) {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const day = String(date.getDate()).padStart(2, '0');
    const month = months[date.getMonth()];
    const year = date.getFullYear();
    return `${day} ${month} ${year}`;
  } catch (e) {
    return dateString;
  }
}

/**
 * Formats confidence score as 0.50
 */
export function formatConfidence(score) {
  if (score === null || score === undefined || isNaN(score)) {
    return '0.00';
  }
  return Number(score).toFixed(2);
}

/**
 * Formats ISO datetime string to readable string
 */
export function formatDateTime(isoString) {
  if (!isoString) return '—';
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    const datePart = formatDate(isoString);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${datePart}, ${hours}:${minutes}`;
  } catch (e) {
    return isoString;
  }
}
