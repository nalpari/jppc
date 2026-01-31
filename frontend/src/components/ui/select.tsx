"use client";

import * as React from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

export interface SelectOption {
  value: string;
  label: string;
  disabled?: boolean;
}

export interface SelectProps {
  options: SelectOption[];
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  className?: string;
}

export function Select({
  options,
  value,
  onChange,
  placeholder = "Select...",
  label,
  error,
  disabled,
  className,
}: SelectProps) {
  return (
    <div className="space-y-1">
      {label && (
        <label className="text-sm font-medium text-foreground">{label}</label>
      )}
      <div className="relative">
        <select
          value={value}
          onChange={(e) => onChange?.(e.target.value)}
          disabled={disabled}
          className={cn(
            "flex h-10 w-full appearance-none rounded-md border border-input bg-background px-3 py-2 pr-10 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive",
            className
          )}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option
              key={option.value}
              value={option.value}
              disabled={option.disabled}
            >
              {option.label}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none" />
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}

export interface MultiSelectProps {
  options: SelectOption[];
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  className?: string;
}

export function MultiSelect({
  options,
  value,
  onChange,
  placeholder = "Select items...",
  label,
  error,
  disabled,
  className,
}: MultiSelectProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const toggleOption = (optionValue: string) => {
    if (value.includes(optionValue)) {
      onChange(value.filter((v) => v !== optionValue));
    } else {
      onChange([...value, optionValue]);
    }
  };

  const selectedLabels = options
    .filter((opt) => value.includes(opt.value))
    .map((opt) => opt.label);

  return (
    <div className="space-y-1" ref={containerRef}>
      {label && (
        <label className="text-sm font-medium text-foreground">{label}</label>
      )}
      <div className="relative">
        <button
          type="button"
          onClick={() => !disabled && setIsOpen(!isOpen)}
          disabled={disabled}
          className={cn(
            "flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive",
            className
          )}
        >
          <span className={cn("truncate", !selectedLabels.length && "text-muted-foreground")}>
            {selectedLabels.length > 0 ? selectedLabels.join(", ") : placeholder}
          </span>
          <ChevronDown className="h-4 w-4 opacity-50" />
        </button>

        {isOpen && (
          <div className="absolute z-50 mt-1 w-full rounded-md border bg-popover shadow-lg">
            <div className="max-h-60 overflow-auto p-1">
              {options.map((option) => (
                <div
                  key={option.value}
                  onClick={() => !option.disabled && toggleOption(option.value)}
                  className={cn(
                    "flex cursor-pointer items-center gap-2 rounded-sm px-2 py-1.5 text-sm hover:bg-accent",
                    option.disabled && "cursor-not-allowed opacity-50",
                    value.includes(option.value) && "bg-accent"
                  )}
                >
                  <input
                    type="checkbox"
                    checked={value.includes(option.value)}
                    onChange={() => {}}
                    className="h-4 w-4"
                    disabled={option.disabled}
                  />
                  {option.label}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </div>
  );
}
