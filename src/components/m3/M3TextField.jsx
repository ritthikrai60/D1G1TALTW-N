import React, { useEffect, useRef } from 'react';
import '@material/web/textfield/outlined-text-field.js';
import '@material/web/textfield/filled-text-field.js';

/**
 * Material 3 Text Field Wrapper
 * @param {'outlined' | 'filled'} variant
 */
export const M3TextField = React.forwardRef(function M3TextField(
  {
    variant = 'outlined',
    label,
    value = '',
    placeholder = '',
    type = 'text',
    disabled = false,
    error = false,
    errorText = '',
    leadingIcon,
    trailingIcon,
    onChange,
    onInput,
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
    if (el.value !== value) el.value = value || '';
  }, [value, elementRef]);

  useEffect(() => {
    const el = elementRef.current;
    if (!el) return;
    const handleInput = (e) => {
      if (onInput) onInput(e.target.value, e);
      if (onChange) onChange(e);
    };
    el.addEventListener('input', handleInput);
    return () => el.removeEventListener('input', handleInput);
  }, [onChange, onInput, elementRef]);

  const Tag = variant === 'filled' ? 'md-filled-text-field' : 'md-outlined-text-field';

  return React.createElement(
    Tag,
    {
      ref: elementRef,
      label,
      placeholder,
      type,
      disabled: disabled ? '' : undefined,
      error: error ? '' : undefined,
      'error-text': errorText || undefined,
      class: className,
      ...props,
    },
    leadingIcon
      ? React.createElement('span', { slot: 'leading-icon', className: 'inline-flex items-center' }, leadingIcon)
      : null,
    trailingIcon
      ? React.createElement('span', { slot: 'trailing-icon', className: 'inline-flex items-center' }, trailingIcon)
      : null
  );
});

export default M3TextField;

