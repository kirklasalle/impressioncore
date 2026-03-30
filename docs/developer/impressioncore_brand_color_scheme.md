# Impressioncore Brand Color Scheme

**Created:** June 08, 2025  
**Updated:** December 29, 2025  
**Author:** Kirk LaSalle; GitHub Copilot  
**Tags:** #ids #standardized_header #docs\developer\impressioncore_brand_color_scheme.md #documentation #web_interface  
**Category:** Developer Documentation  
**Status:** Active
**IDS Integration:** This document is indexed and searchable via the ImpressionCore Documentation System (IDS).

---

Last updated: 2025-06-08
Responsible: @GitHubCopilot & Kirk LaSalle
---

# ImpressionCore Brand Standard Color Scheme

## World-Class Fusion: Noir Sophistication × Early Mickey Mouse × Classic DC Comics

### 🎨 **Design Philosophy**

ImpressionCore's visual identity combines:

- **Noir Sophistication**: High contrast, dramatic shadows, professional gravitas
- **Early Mickey Mouse Comic Joy**: Warm yellows, playful energy, optimistic charm
- **Classic DC Comics Heritage**: Bold primaries, heroic confidence, timeless appeal

---

## 🎭 **Primary Brand Palette**

### **Noir Foundation**

```css
--ic-noir-black: #1a1a1a        /* Deep charcoal, not pure black */
--ic-noir-charcoal: #2d2d2d     /* Secondary dark for depth */
--ic-noir-silver: #c0c0c0       /* Classic silver highlights */
--ic-noir-white: #f8f8f8        /* Warm white, not stark */
```

### **Mickey Mouse Comic Heritage**

```css
--ic-mickey-gold: #ffd700       /* Classic cartoon gold */
--ic-mickey-yellow: #ffeb3b     /* Cheerful comic yellow */
--ic-mickey-cream: #fff8e1      /* Warm background tone */
--ic-mickey-orange: #ff9800     /* Playful accent */
```

### **DC Comics Heroic**

```css
--ic-dc-blue: #1e3a8a          /* Superman's noble blue */
--ic-dc-red: #dc2626           /* Classic comic book red */
--ic-dc-cyan: #0891b2          /* Modern tech cyan */
--ic-dc-purple: #7c3aed        /* Mystical depth */
```

---

## 🌟 **Semantic Color System**

### **Primary Actions & Branding**

```css
--ic-primary: #1e3a8a          /* DC noble blue */
--ic-primary-light: #3b82f6    /* Lighter blue variant */
--ic-primary-dark: #1e40af     /* Darker blue variant */
--ic-accent: #ffd700           /* Mickey gold highlight */
```

### **Interactive States**

```css
--ic-hover: #ffeb3b            /* Mickey yellow on hover */
--ic-active: #dc2626           /* DC red for active states */
--ic-focus: #0891b2            /* Cyan for focus indicators */
--ic-disabled: #9ca3af         /* Muted gray */
```

### **Semantic Meanings**

```css
--ic-success: #059669          /* Professional green */
--ic-warning: #d97706          /* Mickey orange warning */
--ic-error: #dc2626            /* DC red for errors */
--ic-info: #0891b2             /* Cyan for information */
```

### **Text Hierarchy**

```css
--ic-text-primary: #1a1a1a     /* Noir charcoal */
--ic-text-secondary: #4b5563   /* Medium gray */
--ic-text-muted: #9ca3af       /* Light gray */
--ic-text-inverse: #f8f8f8     /* Light text on dark */
```

### **Background System**

```css
--ic-bg-primary: #ffffff       /* Clean white */
--ic-bg-secondary: #f8fafc     /* Subtle off-white */
--ic-bg-accent: #fff8e1        /* Mickey cream */
--ic-bg-dark: #1a1a1a          /* Noir foundation */
--ic-bg-paper: #ffffff         /* Document background */
```

### **Border & Surface**

```css
--ic-border-light: #e5e7eb     /* Subtle borders */
--ic-border-medium: #d1d5db    /* Standard borders */
--ic-border-dark: #6b7280      /* Strong borders */
--ic-shadow-color: rgba(26, 26, 26, 0.1)  /* Noir shadows */
```

---

## 🎨 **Theme Variations**

### **Light Theme (Default)**

- Background: Warm whites and cream tones
- Text: Deep noir charcoal for readability
- Accents: Mickey gold and DC blue
- Mood: Professional yet approachable

### **Dark Theme (Noir Mode)**

- Background: Deep charcoals and blacks
- Text: Silver and warm whites
- Accents: Bright gold and cyan highlights
- Mood: Sophisticated, dramatic, focused

### **High Contrast (Accessibility)**

- Background: Pure white or pure black
- Text: Maximum contrast ratios
- Accents: Bold primary colors only
- Mood: Crystal clear, accessible

---

## 🎭 **Usage Guidelines**

### **Primary Applications**

1. **Headers & Navigation**: Noir black with gold accents
2. **Body Content**: Warm white backgrounds with charcoal text
3. **Interactive Elements**: DC blue with Mickey gold highlights
4. **Status Indicators**: Semantic color system
5. **Code Blocks**: Noir theme with syntax highlighting

### **Brand Personality Expression**

- **Serious Documentation**: Noir-heavy with blue accents
- **User-Friendly Interfaces**: Mickey gold prominence with warm tones
- **Technical Diagrams**: High contrast noir with strategic color highlights
- **Marketing Materials**: Balanced trio of all three influences

### **Accessibility Standards**

- All color combinations meet WCAG AA standards (4.5:1 contrast ratio)
- Color never used as the sole indicator of meaning
- High contrast mode available for enhanced accessibility
- Focus indicators clearly visible in all themes

---

## 🚀 **Implementation Examples**

### **CSS Custom Properties**

```css
:root {
  /* Noir Foundation */
  --ic-noir-black: #1a1a1a;
  --ic-noir-charcoal: #2d2d2d;
  --ic-noir-silver: #c0c0c0;
  --ic-noir-white: #f8f8f8;
  
  /* Mickey Mouse Heritage */
  --ic-mickey-gold: #ffd700;
  --ic-mickey-yellow: #ffeb3b;
  --ic-mickey-cream: #fff8e1;
  --ic-mickey-orange: #ff9800;
  
  /* DC Comics Heroic */
  --ic-dc-blue: #1e3a8a;
  --ic-dc-red: #dc2626;
  --ic-dc-cyan: #0891b2;
  --ic-dc-purple: #7c3aed;
  
  /* Semantic System */
  --ic-primary: var(--ic-dc-blue);
  --ic-accent: var(--ic-mickey-gold);
  --ic-text-primary: var(--ic-noir-black);
  --ic-bg-primary: var(--ic-noir-white);
}
```

### **Component Examples**

```css
/* Header - Noir sophistication */
.header {
  background: linear-gradient(135deg, var(--ic-noir-black), var(--ic-noir-charcoal));
  color: var(--ic-noir-white);
  border-bottom: 3px solid var(--ic-mickey-gold);
}

/* Button - Mickey Mouse charm */
.btn-primary {
  background: var(--ic-dc-blue);
  color: var(--ic-noir-white);
  border: 2px solid var(--ic-mickey-gold);
}

.btn-primary:hover {
  background: var(--ic-mickey-gold);
  color: var(--ic-noir-black);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px var(--ic-shadow-color);
}

/* Content - Professional warmth */
.content {
  background: var(--ic-bg-primary);
  color: var(--ic-text-primary);
  border-left: 4px solid var(--ic-dc-blue);
}
```

---

## 🏆 **Brand Applications**

### **Documentation**

- Headers: Noir black with gold underlines
- Body: Warm white with charcoal text
- Code: High-contrast noir theme
- Highlights: Strategic blue and gold

### **Web Interfaces**

- Navigation: Dark noir with gold accents
- Content areas: Light with blue highlights
- Interactive elements: Mickey gold hover states
- Status: Full semantic color system

### **Diagrams & Visualizations**

- Base: Noir high-contrast foundation
- Highlights: Strategic color for emphasis
- Flow: Grayscale gradients with color accents
- Accessibility: High contrast variants available

---

## 🎨 **Color Psychology & Brand Impact**

### **Noir Sophistication**

- **Black/Charcoal**: Authority, precision, technical excellence
- **Silver**: Innovation, cutting-edge technology, reliability
- **High Contrast**: Clarity, focus, professional confidence

### **Mickey Mouse Joy**

- **Gold**: Optimism, success, premium quality
- **Yellow**: Creativity, energy, approachability
- **Warm Tones**: Friendliness, accessibility, human-centered design

### **DC Comics Heroism**

- **Blue**: Trust, stability, intelligence, heroic purpose
- **Red**: Power, action, determination, breakthrough innovation
- **Bold Contrasts**: Confidence, impact, memorable presence

### **Combined Effect**

The fusion creates a brand that is simultaneously:

- **Technically Sophisticated** (Noir professionalism)
- **Approachably Human** (Mickey warmth)
- **Heroically Ambitious** (DC confidence)
- **Uniquely Memorable** (Distinctive combination)

---

*This color scheme positions ImpressionCore as the sophisticated yet approachable hero of AI democratization - serious enough for enterprise adoption, warm enough for individual users, and bold enough to change the world.*
