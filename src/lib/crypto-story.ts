export function isBitcoinStory(coins:readonly string[],categories:readonly string[]):boolean{
 const hasBitcoinSignal=coins.includes('BTC')||categories.includes('Bitcoin');
 return hasBitcoinSignal&&coins.every(coin=>coin==='BTC');
}
export function isEthereumStory(coins:readonly string[],categories:readonly string[]):boolean{
 const hasEthereumSignal=coins.includes('ETH')||categories.includes('Ethereum');
 return hasEthereumSignal&&coins.every(coin=>coin==='ETH');
}
