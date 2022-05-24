import time
from SX127x.LoRa import *

class LoraRescuer(LoRa):

    rx_data = ''
    tx_data = 'test tx'

    def __init__(self):
        super(LoraRescuer, self).__init__(verbose=False)

        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        
        self.reset_ptr_rx()
        self.tx_data = 'test tx'
    
    
    '''
        當LoRa模式設為RXCONT時便會反覆執行這個方法
    '''
    def on_rx_done(self):
        self.set_mode(MODE.RXCONT)

        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        self.rx_data = ''.join([chr(c) for c in payload])

        print(f'RX: {self.rx_data}')

        # self.set_mode(MODE.STDBY)
    
    
    '''
        當LoRa模式設為TX時便會反覆執行這個方法
    '''
    def on_tx_done(self):
        self.clear_irq_flags(TxDone=1)

        print(f'TX: {self.tx_data}')
        self.write_payload([ord(c) for c in self.tx_data])
        self.set_mode(MODE.TX)
        time.sleep(1)
        