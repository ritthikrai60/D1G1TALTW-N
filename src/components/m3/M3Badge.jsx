import React from 'react';
import '@material/web/labs/badge/badge.js';

/**
 * Material 3 Badge Wrapper
 * @param {string | number} value Text or count to display in badge. If empty, renders as a dot badge.
 */
export const M3Badge = React.forwardRef(function M3Badge(
  { value = '', ariaLabel = '', className = '', ...props },
  ref
) {
  const strVal = value !== null && value !== undefined && value !== '' ? String(value) : '';
  return React.createElement('md-badge', {
    ref,
    value: strVal || undefined,
    'aria-label': ariaLabel || (strVal ? `${strVal} รายการ` : 'แจ้งเตือน'),
    class: className,
    ...props,
  });
});

