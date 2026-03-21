# Schema Templates — Copy-Paste JSON-LD Patterns

## Website Schema (Homepage)

```json
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  "name": "Sweden Sustainability Directory",
  "url": "https://yourdomain.com",
  "description": "Interactive directory of 80+ social and ecological sustainability initiatives across Sweden",
  "inLanguage": ["sv", "en"],
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://yourdomain.com/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

## Organization Listing (Generic)

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "",
  "description": "",
  "url": "",
  "logo": "",
  "foundingDate": "",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "",
    "addressRegion": "",
    "addressCountry": "SE"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 0,
    "longitude": 0
  },
  "areaServed": {
    "@type": "Country",
    "name": "Sweden"
  },
  "keywords": [],
  "sameAs": []
}
```

## NGO / Nonprofit Listing

```json
{
  "@context": "https://schema.org",
  "@type": "NGO",
  "name": "",
  "description": "",
  "url": "",
  "foundingDate": "",
  "nonprofitStatus": "NonprofitType",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "",
    "addressRegion": "",
    "addressCountry": "SE"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 0,
    "longitude": 0
  },
  "areaServed": {
    "@type": "Country",
    "name": "Sweden"
  }
}
```

## Farm / Permaculture Listing

```json
{
  "@context": "https://schema.org",
  "@type": "Farm",
  "name": "",
  "description": "",
  "url": "",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "",
    "addressRegion": "",
    "addressCountry": "SE"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 0,
    "longitude": 0
  }
}
```

## Coliving / Lodging Listing

```json
{
  "@context": "https://schema.org",
  "@type": "LodgingBusiness",
  "name": "",
  "description": "",
  "url": "",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "",
    "addressRegion": "",
    "addressCountry": "SE"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 0,
    "longitude": 0
  },
  "amenityFeature": [
    {
      "@type": "LocationFeatureSpecification",
      "name": "Shared kitchen",
      "value": true
    }
  ]
}
```

## Research Organization

```json
{
  "@context": "https://schema.org",
  "@type": "ResearchOrganization",
  "name": "",
  "description": "",
  "url": "",
  "foundingDate": "",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "",
    "addressRegion": "",
    "addressCountry": "SE"
  }
}
```

## Government Organization / Funding Agency

```json
{
  "@context": "https://schema.org",
  "@type": "GovernmentOrganization",
  "name": "",
  "description": "",
  "url": "",
  "address": {
    "@type": "PostalAddress",
    "addressLocality": "",
    "addressRegion": "",
    "addressCountry": "SE"
  }
}
```

## FAQPage Schema

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is [Organization Name]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Complete, self-contained answer. Must make sense extracted out of context."
      }
    },
    {
      "@type": "Question",
      "name": "Where is [Organization Name] located?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Organization Name] is located in [City], [Region], Sweden."
      }
    },
    {
      "@type": "Question",
      "name": "How can I visit [Organization Name]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Visit their website at [url] for visiting information and contact details."
      }
    }
  ]
}
```

## BreadcrumbList Schema

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://yourdomain.com"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Ecovillages",
      "item": "https://yourdomain.com/ecovillages"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Suderbyn",
      "item": "https://yourdomain.com/ecovillages/suderbyn"
    }
  ]
}
```

## Article Schema (Blog/Guide)

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "",
  "description": "",
  "author": {
    "@type": "Organization",
    "name": "Sweden Sustainability Directory"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Sweden Sustainability Directory",
    "url": "https://yourdomain.com"
  },
  "datePublished": "",
  "dateModified": "",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": ""
  },
  "inLanguage": "en"
}
```

## ItemList Schema (Category/Collection Pages)

```json
{
  "@context": "https://schema.org",
  "@type": "ItemList",
  "name": "Ecovillages in Sweden",
  "description": "Complete list of ecovillages across Sweden",
  "numberOfItems": 15,
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "url": "https://yourdomain.com/ecovillages/suderbyn",
      "name": "Suderbyn"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "url": "https://yourdomain.com/ecovillages/angsbacka",
      "name": "Ängsbacka"
    }
  ]
}
```

## HowTo Schema (Guide Content)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to Visit an Ecovillage in Sweden",
  "description": "Step-by-step guide to planning your visit to a Swedish ecovillage",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Choose an ecovillage",
      "text": "Browse our directory to find an ecovillage that matches your interests."
    },
    {
      "@type": "HowToStep",
      "name": "Check visiting options",
      "text": "Visit the ecovillage's website to see if they offer tours, workshops, or volunteer programs."
    }
  ]
}
```

## Multiple Schemas on One Page

Combine schemas using `@graph`:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "BreadcrumbList",
      "itemListElement": [...]
    },
    {
      "@type": "Organization",
      "name": "...",
      ...
    },
    {
      "@type": "FAQPage",
      "mainEntity": [...]
    }
  ]
}
```

## Implementation in Next.js

```tsx
// app/[category]/[slug]/page.tsx
export default function ListingPage({ params }) {
  const listing = getListingBySlug(params.slug);

  const schema = {
    "@context": "https://schema.org",
    "@graph": [
      buildBreadcrumbSchema(listing),
      buildOrganizationSchema(listing),
      buildFAQSchema(listing),
    ],
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      {/* Page content */}
    </>
  );
}
```
