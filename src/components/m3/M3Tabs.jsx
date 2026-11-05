import React, { useEffect, useRef } from 'react';
import '@material/web/tabs/tabs.js';
import '@material/web/tabs/primary-tab.js';
import '@material/web/tabs/secondary-tab.js';

/**
 * Material 3 Tabs Wrapper
 */
export const M3Tabs = React.forwardRef(function M3Tabs(
  {
    activeTabIndex = 0,
    onChange,
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
    el.activeTabIndex = activeTabIndex;
  }, [activeTabIndex, elementRef]);

  useEffect(() => {
    const el = elementRef.current;
    if (!el || !onChange) return;
    const handleChange = () => onChange(el.activeTabIndex);
    el.addEventListener('change', handleChange);
    return () => el.removeEventListener('change', handleChange);
  }, [onChange, elementRef]);

  return React.createElement(
    'md-tabs',
    {
      ref: elementRef,
      class: className,
      ...props,
    },
    children
  );
});

export const M3PrimaryTab = React.forwardRef(function M3PrimaryTab(
  {
    children,
    icon,
    className = '',
    ...props
  },
  ref
) {
  return React.createElement(
    'md-primary-tab',
    {
      ref,
      class: className,
      ...props,
    },
    icon ? React.createElement('span', { slot: 'icon', className: 'inline-flex items-center' }, icon) : null,
    children
  );
});

export default M3Tabs;

