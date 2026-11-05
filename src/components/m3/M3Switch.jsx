import React, { useEffect, useRef } from 'react';
import '@material/web/switch/switch.js';

export const M3Switch = React.forwardRef(function M3Switch(
  {
    selected = false,
    disabled = false,
    icons = true,
    onChange,
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
    el.selected = Boolean(selected);
  }, [selected, elementRef]);

  useEffect(() => {
    const el = elementRef.current;
    if (!el || !onChange) return;
    const handleChange = (e) => onChange(el.selected, e);
    el.addEventListener('change', handleChange);
    return () => el.removeEventListener('change', handleChange);
  }, [onChange, elementRef]);

  return React.createElement('md-switch', {
    ref: elementRef,
    selected: selected ? '' : undefined,
    disabled: disabled ? '' : undefined,
    icons: icons ? '' : undefined,
    class: className,
    ...props,
  });
});

export default M3Switch;

