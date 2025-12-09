export type AssetType = 'kr-stock' | 'us-stock' | 'crypto';            
                                                                       
export interface Asset {                                               
  id: string | number;                                                 
  name: string;                                                        
  symbol?: string;                                                     
  currentPrice?: number;                                               
  change?: number;                                                     
  changePercent?: number;                                              
  volume?: number;                                                     
  marketCap?: number;                                                  
  [key: string]: any;                                                  
}                                                                      
                                                                       
export interface AssetDetail extends Asset {                           
  description?: string;                                                
  sector?: string;                                                     
  industry?: string;                                                   
}                                                                      
                                                                       
export interface PriceData {                                           
  trade_date: string;                                                  
  open_price: number;                                                  
  high_price: number;                                                  
  low_price: number;                                                   
  close_price: number;                                                 
  volume: number;                                                      
}                                                                      
                                                                       
export interface AssetState {                                          
  items: Asset[];                                                      
  isLoading: boolean;                                                  
  error: string | null;                                                
}
