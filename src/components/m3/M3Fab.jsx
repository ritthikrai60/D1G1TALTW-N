import React, { useEffect, useRef } from 'react';
import '@material/web/fab/fab.js';

/**
 * Material 3 Floating Action Button Wrapper
 * @param {'surface' | 'primary' | 'secondary' | 'tertiary'} variant
 * @param {'small' | 'medium' | 'large'} size
 */
export const M3Fab = React.forwardRef(function M3Fab(
  {
    variant = 'primary',
    size = 'medium',
    label,
    icon,
    lowered = false,
    className = '',
    onClick,
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
    'md-fab',
    {
      ref: elementRef,
      variant,
      size,
      label: label || undefined,
      lowered: lowered ? '' : undefined,
      class: className,
      ...props,
    },
    icon ? React.createElement('span', { slot: 'icon', className: 'inline-flex items-center justify-center' }, icon) : null
  );
});

export default M3Fab;

