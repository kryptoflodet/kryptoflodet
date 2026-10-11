import raw from '../../public/data/market.json';
import {normalizeMarket,type MarketData} from './market';
const imported=normalizeMarket(raw);
// Saved real quotes remain explicitly stale until a fresh request succeeds.
export const initialMarket:MarketData={...imported,mode:'stale',fetchedAt:new Date(Math.min(...imported.quotes.flatMap(q=>q.updatedAt?[Date.parse(q.updatedAt)]:[]))).toISOString()};
