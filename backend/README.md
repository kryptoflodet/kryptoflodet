# Bevarad backendkod

Detta är projektets ursprungliga serverdel för Vinext/Cloudflare Workers: API-rutter, Drizzle/D1-schema, migreringar, repository och gränssnitt för framtida nyhetsimport.

GitHub Pages är statisk hosting och exekverar inte dessa filer. Frontendens aktiva marknadsadapter finns i `src/lib/market-client.ts`; demonyheterna läses från `src/lib/demo.ts`.

En framtida serverdistribution kräver en separat Workers/Vinext-konfiguration, D1-bindningen `DB`, Drizzle, konfigurerade importkällor och aliaset `@` mot denna backendkatalog. Filerna är bevarad källkod och ingen färdig separat driftmiljö. Inga åtkomstnycklar eller tidigare hostingidentiteter ingår.
