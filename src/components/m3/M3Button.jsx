import React, { useEffect, useRef } from 'react';
import '@material/web/button/filled-button.js';
import '@material/web/button/outlined-button.js';
import '@material/web/button/filled-tonal-button.js';
import '@material/web/button/text-button.js';
import '@material/web/button/elevated-button.js';

/**
 * Material 3 Button Wrapper
 * @param {'filled' | 'outlined' | 'tonal' | 'text' | 'elevated'} variant
 */
export const M3Button = React.forwardRef(function M3Button(
  {
    variant = 'filled',
    children,
    icon,
    trailingIcon = false,
    disabled = false,
    className = '',
    onClick,
    type = 'button',
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

  const Tag =
    variant === 'outlined'
      ? 'md-outlined-button'
      : variant === 'tonal'
      ? 'md-filled-tonal-button'
      : variant === 'text'
      ? 'md-text-button'
      : variant === 'elevated'
      ? 'md-elevated-button'
      : 'md-filled-button';

  return React.createElement(
    Tag,
    {
      ref: elementRef,
      disabled: disabled ? '' : undefined,
      'has-icon': icon ? '' : undefined,
      'trailing-icon': trailingIcon ? '' : undefined,
      class: className,
      type,
      ...props,
    },
    icon ? React.createElement('span', { slot: 'icon', className: 'inline-flex items-center' }, icon) : null,
    children
  );
});

export default M3Button;

