/** @type {import('tailwindcss').Config} */

// Design-system token safelist.
//
// A2UI payloads (deterministic backend + LLM output) carry className strings
// that only exist at RUNTIME - Tailwind's content scan of ./src never sees
// them, so every Apple/Astryx token the Design Director prompt and the
// deterministic payloads use must be compiled up-front via safelist.
// Keep this in sync with backend/app/agent/prompts/apple_designer.py
// ("Class discipline" section).

const zinc = ['zinc-50', 'zinc-100', 'zinc-200', 'zinc-300', 'zinc-400', 'zinc-500', 'zinc-600', 'zinc-700', 'zinc-800', 'zinc-900', 'zinc-950'];
const accents = [
  'white', 'black',
  'emerald-50', 'emerald-100', 'emerald-200', 'emerald-700',
  'rose-50', 'rose-100', 'rose-200', 'rose-700',
  'blue-50', 'blue-100', 'blue-200', 'blue-500', 'blue-700',
  'amber-50', 'amber-100', 'amber-300', 'amber-800',
];
const colors = [...zinc, ...accents];

const spacing = ['0', '0.5', '1', '1.5', '2', '2.5', '3', '3.5', '4', '5', '6', '7', '8', '9', '10', '12', '14', '16', '20', '24', '28', '32', '36', '40', '44', '48'];

const safelist = [];

// Colors + common color variants
for (const c of colors) {
  safelist.push(`bg-${c}`, `text-${c}`, `border-${c}`, `ring-${c}`, `divide-${c}`);
  safelist.push(`hover:bg-${c}`, `hover:text-${c}`, `hover:border-${c}`, `placeholder-${c}`);
}
// Opacity-modified colors the deterministic payloads / prompt rely on.
for (const op of ['80', '90', '70', '60', '50']) {
  safelist.push(`bg-white/${op}`, `bg-black/${op}`, `bg-zinc-50/${op}`, `bg-zinc-100/${op}`);
  for (const c of ['zinc-200', 'zinc-300', 'zinc-100', 'white', 'black']) {
    safelist.push(`border-${c}/${op}`);
  }
}

// Spacing scale (padding / margin / gap / space-y-x)
for (const s of spacing) {
  for (const prefix of ['p', 'px', 'py', 'pt', 'pr', 'pb', 'pl', 'ps', 'pe']) {
    safelist.push(`${prefix}-${s}`);
  }
  for (const prefix of ['m', 'mx', 'my', 'mt', 'mr', 'mb', 'ml', 'ms', 'me']) {
    safelist.push(`${prefix}-${s}`);
  }
  safelist.push(`gap-${s}`, `space-y-${s}`, `space-x-${s}`);
}
// Semantic gap tokens the catalog + prompt use ("sm" | "md" | "lg" as literals
// get mapped by renderers; keep the literal classes available too, in case
// an LLM emits them directly).
safelist.push('gap-sm', 'gap-md', 'gap-lg', 'space-y-sm', 'space-y-md', 'space-y-lg');

// Typography
for (const size of ['xs', 'sm', 'base', 'lg', 'xl', '2xl', '3xl', '4xl', '5xl', '6xl', '7xl']) {
  safelist.push(`text-${size}`);
}
safelist.push(
  'font-normal', 'font-medium', 'font-semibold', 'font-bold', 'font-extrabold', 'font-mono',
  'text-center', 'text-left', 'text-right',
  'uppercase', 'lowercase', 'capitalize', 'normal-case',
  'tracking-tighter', 'tracking-tight', 'tracking-normal', 'tracking-wide', 'tracking-wider', 'tracking-widest',
  'leading-none', 'leading-tight', 'leading-snug', 'leading-normal', 'leading-relaxed', 'leading-loose',
);

// Layout
safelist.push(
  'flex', 'inline-flex', 'block', 'inline-block', 'grid', 'hidden',
  'relative', 'absolute', 'fixed', 'sticky',
  'overflow-hidden', 'overflow-auto', 'overflow-x-auto', 'overflow-x-scroll',
  'flex-wrap', 'flex-nowrap', 'flex-col', 'flex-row', 'flex-1', 'grow', 'shrink',
  'items-start', 'items-center', 'items-end',
  'justify-start', 'justify-center', 'justify-end', 'justify-between', 'justify-around',
  'w-full', 'h-full', 'h-auto', 'w-auto', 'w-fit',
  'max-w-sm', 'max-w-md', 'max-w-lg', 'max-w-xl', 'max-w-2xl', 'max-w-3xl', 'max-w-4xl', 'max-w-5xl', 'max-w-6xl', 'max-w-7xl', 'max-w-full', 'max-w-screen-sm', 'max-w-screen-md', 'max-w-screen-lg', 'max-w-screen-xl', 'max-w-3xl',
  'mx-auto', 'my-auto', 'isolate', 'z-0', 'z-10', 'z-20', 'z-50', 'z-auto',
);

// Grid
safelist.push(
  'grid-cols-1', 'grid-cols-2', 'grid-cols-3', 'grid-cols-4', 'grid-cols-5', 'grid-cols-6',
  'md:grid-cols-1', 'md:grid-cols-2', 'md:grid-cols-3', 'lg:grid-cols-1', 'lg:grid-cols-2', 'lg:grid-cols-3', 'lg:grid-cols-4',
  'md:flex-row', 'md:flex-col',
);

// Responsive type + spacing variants the prompt recommends
safelist.push(
  'md:text-2xl', 'md:text-3xl', 'md:text-4xl', 'md:text-5xl', 'md:text-6xl',
  'lg:text-3xl', 'lg:text-4xl', 'lg:text-5xl',
  'md:py-12', 'md:py-16', 'md:py-24', 'md:px-12', 'md:px-16',
  'md:space-y-8', 'md:gap-8', 'md:w-1/2', 'md:w-2/3', 'md:w-3/4',
  'w-1/2', 'w-1/3', 'w-2/3', 'w-3/4', 'w-1/4', 'w-full', 'w-auto',
);

// Rounding / elevation / ring
safelist.push(
  'rounded-none', 'rounded-sm', 'rounded', 'rounded-md', 'rounded-lg', 'rounded-xl', 'rounded-2xl', 'rounded-3xl', 'rounded-full',
  'shadow-sm', 'shadow', 'shadow-md', 'shadow-lg', 'shadow-xl', 'shadow-2xl', 'shadow-none',
  'ring', 'ring-0', 'ring-1', 'ring-2', 'ring-4', 'ring-8', 'ring-offset-2', 'ring-offset-4', 'ring-offset-white',
);
// Arbitrary shadow / ring / scale values used by the Apple component styling
// (e.g. shadow-[0_2px_8px_rgba(0,0,0,0.12)], active:scale-[0.98]).
safelist.push({
  pattern: /^shadow-\[(?:[0-9]+px\s)+[0-9]+px_?rgba?\([^)]*\)\]$/,
});

// Effects
safelist.push(
  'transition', 'transition-all', 'transition-colors', 'transition-transform', 'transition-shadow',
  'duration-75', 'duration-100', 'duration-150', 'duration-200', 'duration-300', 'duration-500', 'duration-700',
  'ease-in', 'ease-out', 'ease-in-out', 'ease-linear',
  'hover:scale-105', 'active:scale-98', 'active:scale-[0.98]',
  'backdrop-blur', 'backdrop-blur-sm', 'backdrop-blur-md', 'backdrop-blur-lg',
  'opacity-40', 'opacity-50', 'opacity-60', 'opacity-70', 'opacity-80', 'opacity-90',
  'select-none', 'select-text', 'cursor-pointer', 'cursor-default', 'cursor-not-allowed',
  'border', 'border-0', 'border-2', 'border-4', 'border-t', 'border-b', 'border-l', 'border-r',
  'divide-y', 'divide-x',
  'object-cover', 'object-contain', 'object-center',
);

export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  safelist,
  theme: {
    extend: {},
  },
  plugins: [],
};
