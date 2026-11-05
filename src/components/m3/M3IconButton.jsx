import React, { useEffect, useRef } from 'react';
import '@material/web/iconbutton/icon-button.js';
import '@material/web/iconbutton/filled-icon-button.js';
import '@material/web/iconbutton/filled-tonal-icon-button.js';
import '@material/web/iconbutton/outlined-icon-button.js';

/**
 * Material 3 Icon Button Wrapper
 * @param {'standard' | 'filled' | 'tonal' | 'outlined'} variant
 * @param {boolean} toggle Whether this is a toggleable icon button
 * @param {boolean} selected Current toggle state
 * @param {string} ariaLabel Accessible label (mandatory for icon-only buttons)
 */
export const M3IconButton = React.forwardRef(function M3IconButton(
  {
    variant = 'standard',
    toggle = false,
    selected = false,
    disabled = false,
    ariaLabel = '',
    className = '',
    onClick,
    children,
    title = '',
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

  useEffect(() => {
    const el = elementRef.current;
    if (!el) return;
    if (toggle) {
      el.selected = Boolean(selected);
    }
  }, [toggle, selected, elementRef]);

  const Tag =
    variant === 'filled'
      ? 'md-filled-icon-button'
      : variant === 'tonal'
      ? 'md-filled-tonal-icon-button'
      : variant === 'outlined'
      ? 'md-outlined-icon-button'
      : 'md-icon-button';

  return React.createElement(
    Tag,
    {
      ref: elementRef,
      toggle: toggle ? '' : undefined,
      selected: toggle && selected ? '' : undefined,
      disabled: disabled ? '' : undefined,
      'aria-label': ariaLabel || title,
      'aria-pressed': toggle ? String(Boolean(selected)) : undefined,
      title: title || ariaLabel,
      class: className,
      ...props,
    },
    children
  );
});

