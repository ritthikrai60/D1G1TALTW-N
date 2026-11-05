import React, { useEffect, useRef } from 'react';
import '@material/web/chips/chip-set.js';
import '@material/web/chips/filter-chip.js';
import '@material/web/chips/assist-chip.js';

export const M3ChipSet = React.forwardRef(function M3ChipSet(
  { children, className = '', ...props },
  ref
) {
  return React.createElement('md-chip-set', { ref, class: className, ...props }, children);
});

export const M3FilterChip = React.forwardRef(function M3FilterChip(
  {
    label,
    selected = false,
    disabled = false,
    icon,
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
    'md-filter-chip',
    {
      ref: elementRef,
      label,
      selected: selected ? '' : undefined,
      disabled: disabled ? '' : undefined,
      class: className,
      ...props,
    },
    icon ? React.createElement('span', { slot: 'icon', className: 'inline-flex items-center' }, icon) : null
  );
});

export const M3AssistChip = React.forwardRef(function M3AssistChip(
  {
    label,
    disabled = false,
    icon,
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
    'md-assist-chip',
    {
      ref: elementRef,
      label,
      disabled: disabled ? '' : undefined,
      class: className,
      ...props,
    },
    icon ? React.createElement('span', { slot: 'icon', className: 'inline-flex items-center' }, icon) : null
  );
});

export default { M3ChipSet, M3FilterChip, M3AssistChip };

