import React, { useEffect, useRef } from 'react';
import '@material/web/menu/menu.js';
import '@material/web/menu/menu-item.js';

export const M3Menu = React.forwardRef(function M3Menu(
  {
    open = false,
    anchor,
    onClose,
    children,
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
    if (anchor) {
      if (typeof anchor === 'string') {
        el.anchor = anchor;
      } else if (anchor instanceof HTMLElement) {
        el.anchorElement = anchor;
      }
    }
  }, [anchor, elementRef]);

  useEffect(() => {
    const el = elementRef.current;
    if (!el) return;
    el.open = Boolean(open);
  }, [open, elementRef]);

  useEffect(() => {
    const el = elementRef.current;
    if (!el || !onClose) return;
    const handleClosed = (e) => onClose(e);
    el.addEventListener('closed', handleClosed);
    return () => el.removeEventListener('closed', handleClosed);
  }, [onClose, elementRef]);

  return React.createElement('md-menu', {
    ref: elementRef,
    open: open ? '' : undefined,
    class: className,
    ...props,
  }, children);
});

export const M3MenuItem = React.forwardRef(function M3MenuItem(
  {
    children,
    headline,
    icon,
    disabled = false,
    onClick,
    className = '',
    ...props
  },
  ref
) {
  const innerRef = useRef(null);
  const elementRef = ref || innerRef;

  useEffect(() => {
    const el = elementRef.current;
    if (!el || !onClick) return;
    const handleClick = (e) => onClick(e);
    el.addEventListener('click', handleClick);
    return () => el.removeEventListener('click', handleClick);
  }, [onClick, elementRef]);

  return React.createElement(
    'md-menu-item',
    {
      ref: elementRef,
      disabled: disabled ? '' : undefined,
      class: className,
      ...props,
    },
    icon ? React.createElement('span', { slot: 'start', className: 'inline-flex items-center mr-2' }, icon) : null,
    headline ? React.createElement('div', { slot: 'headline' }, headline) : null,
    children
  );
});

export default { M3Menu, M3MenuItem };

