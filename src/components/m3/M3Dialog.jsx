import React, { useEffect, useRef } from 'react';
import '@material/web/dialog/dialog.js';

/**
 * Material 3 Dialog Wrapper
 */
export const M3Dialog = React.forwardRef(function M3Dialog(
  {
    open = false,
    onClose,
    headline,
    icon,
    children,
    actions,
    className = '',
    ...props
  },
  ref
) {
  const innerRef = useRef(null);
  const elementRef = ref || innerRef;

  useEffect(() => {
    const el = elementRef.current;
    if (!el) return;
    if (open) {
      if (!el.open) el.show();
    } else {
      if (el.open) el.close();
    }
  }, [open, elementRef]);

  useEffect(() => {
    const el = elementRef.current;
    if (!el || !onClose) return;
    const handleClosed = (e) => onClose(e);
    el.addEventListener('closed', handleClosed);
    return () => el.removeEventListener('closed', handleClosed);
  }, [onClose, elementRef]);

  return React.createElement(
    'md-dialog',
    {
      ref: elementRef,
      class: className,
      ...props,
    },
    icon ? React.createElement('div', { slot: 'icon', className: 'inline-flex items-center justify-center' }, icon) : null,
    headline ? React.createElement('div', { slot: 'headline', className: 'text-lg font-bold' }, headline) : null,
    React.createElement('div', { slot: 'content', className: 'm3-dialog-content' }, children),
    actions ? React.createElement('div', { slot: 'actions', className: 'flex items-center gap-2 justify-end' }, actions) : null
  );
});

export default M3Dialog;

