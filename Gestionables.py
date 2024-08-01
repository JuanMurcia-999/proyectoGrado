from pysnmp.smi.rfc1902 import ObjectIdentity, ObjectType
from slim.slim_get import slim_get
import asyncio


ifInOctets='1.3.6.1.2.1.2.2.1.10'
ifOutOctets ='1.3.6.1.2.1.2.2.1.16'
Num_Interface='12'
intervalo = 10


async def peticion(community,host,port):
     return await slim_get(
                community, host, port,
                ObjectType(ObjectIdentity(ifInOctets+'.'+Num_Interface)),
                ObjectType(ObjectIdentity(ifOutOctets+'.'+Num_Interface))
            )
    

async def AnchoBanda():
    while True: 
        community='public'
        host='192.168.20.25'
        port=161
        InOut1=[]
        InOut2=[]

        varbinds = await peticion(community,host,port)
        for varBind in varbinds:
            _, value = varBind
            InOut1.append(int(value))
            
        await asyncio.sleep(intervalo)
        
        varbinds = await peticion(community,host,port)
        for varBind in varbinds:
            _, value = varBind
            InOut2.append(int(value))
        

       
            

        [difIn,difOut] = InOut2[0] - InOut1[0],InOut2[1] - InOut1[1]
        [difInbits,difOutbits] = difIn*8,difOut*8
        in_bps= difInbits / intervalo
        out_bps= difOutbits /intervalo

        [in_kbps,out_kbps]= in_bps/1000,out_bps/1000

        print(f'Kbps IN: {in_kbps} /// Kbps OUT {out_kbps}')
       

       # await asyncio.sleep(intervalo)
async def cosas():
    while True:
        await asyncio.sleep(1)
        print('haciendo cosas de momento')

async def main():
    ancho_banda_task = asyncio.create_task(AnchoBanda())
    cosas_task = asyncio.create_task(cosas())
    await asyncio.gather(ancho_banda_task, cosas_task)


asyncio.run(main())