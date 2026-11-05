import React from 'react';
import '@material/web/divider/divider.js';

/**
 * Material 3 Divider Wrapper
 */
export const M3Divider = React.forwardRef(function M3Divider(
  { inset = false, insetStart = false, insetEnd = false, className = '', ...props },
  ref
) {
  return React.createElement('md-divider', {
    ref,
    inset: inset ? '' : undefined,
    'inset-start': insetStart ? '' : undefined,
    'inset-end': insetEnd ? '' : undefined,
    class: className,
    ...props,
  });
});

