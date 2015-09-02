from pytz import timezone  
import datetime
import pandas as pd
import math

def initialize(context):
    context.security = symbol('AAPL')
    context.limitPrice = None
    context.breachpoint = None
    
def handle_data(context, data):
    p = data[context.security].price  
    exchange_time = get_datetime().astimezone(timezone('US/Eastern'))     
    context.breachpoint = data[context.security].low * 0.95     
    context.target = p + ((p - context.breachpoint) * 0.618)
    context.limitPrice= context.breachpoint * (1 - 0.005)  
    # retrieve all the open orders and log the total open amount  
    # for each order  
    open_aapl_orders = get_open_orders(context.security)  
    if open_aapl_orders:
       for security, orders in open_aapl_orders.iteritems():  
            # iterate over the orders  
            for oo in orders:  
                message = 'Open order for {amount} shares in {stock}'  
                message = message.format(amount=oo.amount, stock=security)  
                log.info(message)
        
    if context.portfolio.positions[context.security].amount is 0 and (not open_aapl_orders or len(open_aapl_orders) <1) :
        context.order_id=order_target_percent(context.security, 1)    
        context.shares_traded= math.floor(context.portfolio.portfolio_value/p)
        #place the lower limit or stop loss order
        context.stop = order_target_percent(context.security, 0.0, style=StopLimitOrder(context.limitPrice,context.breachpoint ) )
        #place the target limit order
        context.tgt = order_target_percent(context.security, 0.0, style=LimitOrder(context.target ) )
    
        log.info('{} Breached High of  {:+.2f} , so bought {} shares @ {:+.2f}, set stop @ {:+.2f} limit {:+.2f}, set target @ {:+.2f}'.format(exchange_time,p,context.shares_traded,p,context.breachpoint,context.limitPrice,context.target))
        tallyResults(context,context.order_id,context.security)
 

def tallyResults(context,order_id, security):
            order_data = get_order(order_id)
            #log.info(order_data)
            if order_data is None:
                log.info("No order found.")
                return 
            
            if order_data['status'] == 1:
                log.info("Order is filled.")
                log.info('Total commission: '+str(order_data['commission']))
                log.info('Commission per share: '+str(order_data['commission']/order_data['filled']))
                log.info('Cost basis: '+str(context.portfolio.positions[security].cost_basis))
            else:
                log.info("Order isn't filled yet.")
            log.info('-------------------------------')  
  