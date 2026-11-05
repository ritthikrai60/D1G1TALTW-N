import React, { useEffect, useRef } from 'react';
import '@material/web/labs/segmentedbuttonset/outlined-segmented-button-set.js';
import '@material/web/labs/segmentedbutton/outlined-segmented-button.js';

/**
 * Material 3 Segmented Button Set Wrapper
 */
export const M3SegmentedButtonSet = React.forwardRef(function M3SegmentedButtonSet(
  { multiselect = false, className = '', children, ...props },
  ref
) {
  return React.createElement(
    'md-outlined-segmented-button-set',
    {
      ref,
      multiselect: multiselect ? '' : undefined,
      class: className,
      ...props,
    },
    children
  );
});

/**
 * Material 3 Outlined Segmented Button Wrapper
 */
export const M3SegmentedButton = React.forwardRef(function M3SegmentedButton(
  {
    label = '',
    selected = false,
    disabled = false,
    noCheckmark = true,
    icon = null,
    onClick,
    className = '',
    ariaLabel = '',
    title = '',
    children,
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
    el.selected = Boolean(selected);
  }, [selected, elementRef]);

  return React.createElement(
    'md-outlined-segmented-button',
    {
      ref: elementRef,
      label,
      selected: selected ? '' : undefined,
      disabled: disabled ? '' : undefined,
      'no-checkmark': noCheckmark ? '' : undefined,
      'has-icon': icon ? '' : undefined,
      'aria-label': ariaLabel || label || title,
      'aria-pressed': String(Boolean(selected)),
      title: title || ariaLabel || label,
      class: className,
      ...props,
    },
    icon ? React.createElement('span', { slot: 'icon', className: 'inline-flex items-center text-sm' }, icon) : null,
    children
  );
});

