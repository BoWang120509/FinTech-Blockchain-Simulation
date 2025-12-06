from blockU import Block
import random
import numpy as np
import time

#这个就是第二主模块，blockchain主要区块。
#如果说block是单独一个区块，那么blockchain部分就是作为整个系统的数据结构+区块管理器+维护者+逻辑执行+未来LCR执行环境。
#所以blockchain的主要作用是负责创造真实使用的创世区块，顺序添加区块，检查区块有效性，保证链的完整性，以及添加的PoW以及处理分叉。
##下一步，在我完成构建blockchain主要架构之后，PoW的加入主要就是让区块不能随意伪造，安全机制的存在。
###再下一步，是构建MemPool。干啥用的呢？就是一个全网共享但不完全一致的交易池。新交易先进入pool，然后矿工选择交易打包区块，fork的时候未选中的交易重新进入pool。
###为了是模拟双花，模拟分叉，模拟交易流动。
###同时，还加入了检查账户余额部分，目的是过滤因余额不足而进行非法交易的情况。
####接下来我加入了分叉，LCR，并且构建双花机制。比比看谁的链长。
####首先是构建多链，从同一个起点开始，攻击者会创建冲突交易。紧接着两个矿工同时挖区块打包交易，开始分叉。
####互相比较链的长度，如果攻击者赢了，触发重组。
####在这里我遇到了问题，因为我的链只有出现交易才挖矿，导致挖矿次数远远多余交易量，mempool变空，挖矿失败，诚实矿工和攻击者都停在少量区块上，双花失败。
####因此我在下面加入了一个自动随机交易的机制，让链不会空。
####再者就是出现了attacker手里余额少的问题。这也正常，主要是因为初始余额就少，再加上后面是随机交易，参与交易次数少，很自然的余额就少。
#####重要的一个改动，就是我加入了时间机制，每次挖矿生成mining_time且服从指数分布。谁的时间用的少，谁就能挖到真正的区块。所以最后时间到了比较，自然就可以产生分叉。
#####此外，必须将不同矿工的挖矿循环分开，也就是说攻击者和诚实者的挖矿进度独立前进，让链的结果自然分裂，尽量的贴合现实世界中网格分裂且互相竞争的情况。
class Blockchain:
    def __init__(self, difficulty=4, miner_hashrate=1.0, name="Honest"):
        """
        这个东西是区块链结构的基本构造函数。包含区块列表以及初始化创建创世区块。
        之后还定义了三个关键的步骤：
        1. 建链。
        2. 返回最后一个区块。
        3. 添加新区块的主要逻辑。
        设定了一个PoW难度，默认hash必须以4个0开头。
        加入了存储待确认交易。然后还有检查账户余额的状态表以及必要的挖矿奖励。
        """
        self.chain = []
        self.difficulty = difficulty
        self.mempool = []
        self.create_genesis_block()
        self.balances = {}
        self.miner_hashrate = miner_hashrate#真实算力基础
        self.name = name
        
        #账户初始余额，等价于真实ETH的创世状态。也就是链刚启动的时候的起点。
        #可以理解为ETH在早期某些地址持有多少ETH。
        #账户余额可以更改。
        self.genesis_balances = {
            "AAAAA": 100,
            "BBBBB": 100,
            "CCCCC": 100,
            "DDDDD": 100,
            "EEEEE": 100,
            "AttackerWallet": 0,
            "Miner": 0
        }
        
        self.balances = self.genesis_balances.copy()
        self.block_reward = 10 #挖矿奖励，自己想改多少改多少。

    def create_genesis_block(self):
        """
        创建创世区块（链上第一个块），真正投入使用的。
        """
        genesis_block = Block(
            index=0,
            transactions=[],
            previous_hash="0" * 64
        )
        
        #对创世块计算hash
        genesis_block.hash = genesis_block.compute_hash()
        
        #添加到主链
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        """
        返回链上的最后一个区块。
        #@property是AI推荐，主要是因为lask block作为一个属性存在，且方便对未来扩展，检查有效性。
        """
        return self.chain[-1]
    

####################################################################  
############################MemPool的添加###########################
####################################################################  
    def add_transaction(self, sender, receiver, amount):
        """
        将一笔交易加入交易池（mempool）。
        这里强调了交易池需要dict格式。原本为了方便测试这里的交易是纯文本，现在改成了正式的dict。
        主要是为了给之后的账户模型，双花，分叉做准备。
        """
        tx = {
            "from": sender,
            "to": receiver,
            "amount": amount
        }
        self.mempool.append(tx)
        print(f"Transaction added to mempool: {tx}")
        
        
    def is_valid_transaction(self, tx):
        """
        校验交易余额是否足够。如果余额不足，交易不应被打包进区块。
        """
        sender = tx["from"]
        amount = tx["amount"]
    
        #账户不存在，视为余额为0
        if sender not in self.balances:
            return False
    
        return self.balances[sender] >= amount

####################################################################  
############################MemPool新增函数截止######################
####################################################################  
 
    #自动交易函数
    def generate_random_transaction(self):
        accounts = list(self.balances.keys())
        sender = random.choice(accounts)
        receiver = random.choice([a for a in accounts if a != sender])
        amount = random.randint(1, 50)
        
        #余额不足取消交易，不加入mempool
        if self.balances.get(sender, 0) < amount:
            return
    
        tx = {"from": sender, "to": receiver, "amount": amount}
        self.mempool.append(tx)
        print(f"Random transaction added: {tx}")
    
    #自动生成 + 挖矿函数
    def auto_generate_and_mine(self, rounds=1):
        for _ in range(rounds):
            self.generate_random_transaction()
            self.mine_block()
    
####################################################################
#########################PoW的核心逻辑层#############################
####################################################################
    def proof_of_work(self, block):
        """
        这个部分是PoW的核心逻辑，按照我在block文件里的说法：
        1. 不断修改nonce。
        2. 重复计算hash。
        3. 直到满足hash以difficulty个 '0' 开头。
        总的来说，就是修改nonce，重复计算hash，难度越高时间越长，找到合法hash标注工作量，其他节点验证。
        加入了升级版本，使用exponential distribution, 还引入了挖矿时间Mining time = Exp(lambda = miner_hashrate).
        属于是算力越大，期望挖矿时间越短。nonce仍然参与，但不再作为时间流逝，而是作为结果记录。
        """
        block.nonce = 0
        computed_hash = block.compute_hash()
        mining_time = np.random.exponential(1.0 / self.miner_hashrate)
             
        while not computed_hash.startswith("0" * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        
        block.mining_time = mining_time
    
        return computed_hash, mining_time

    def add_block(self, block, proof):
        """
        添加一个已经通过了PoW挖矿的区块到链上。在骨架加入了PoW之后，这部分就干两个事儿：
        1. 校验previous_hash。
        2. 校验proof满不满足难度。
        """
        previous_hash_correct = block.previous_hash == self.last_block.hash
        if not previous_hash_correct:
            print("Previous hash incorrect. Block rejected.")
            return False

        #校验PoW
        if not proof.startswith("0" * self.difficulty):
            print("Invalid PoW. Block rejected.")
            return False

        #通过验证，正式写入hash
        block.hash = proof
        self.chain.append(block)
        self.apply_transactions(block.transactions)
        return True   
     
    def apply_transactions(self, tx_list):
        """
        将一个区块中的所有交易更新到账户余额。
        必须写明不允许为负数，余额不足跳过交易。
        """
        for tx in tx_list:
            sender = tx["from"]
            receiver = tx["to"]
            amount = tx["amount"]
    
            #初始化账户
            if sender not in self.balances and sender != "COINBASE":
                self.balances[sender] = 0
            if receiver not in self.balances:
                self.balances[receiver] = 0
            
            #如果是挖矿奖励的话，不扣sender
            if sender == "COINBASE":
                self.balances[receiver] += amount
                continue
                
            #余额不足不执行
            if self.balances.get(sender, 0) < amount:
                print(f"Skipping invalid tx due to insufficient balance: {tx}")
                continue
    
            #扣钱 + 加钱
            self.balances[sender] -= amount
            self.balances[receiver] += amount
            
            
#################################################################### 
######################PoW+Mempool部分截止于此########################
####################################################################    


#################################################################### 
#########################Fork + LCR扩展部分#########################
####################################################################   
    def replace_chain(self, new_chain):
        """
        将当前链替换为更长的新链，并重新计算账户余额。
        用于 LCR和链重组。
        """
        if len(new_chain) <= len(self.chain):
            print("Replacement failed: new chain is not longer.")
            return False
    
        print("Replacing chain with new longer chain")
    
        #替换链
        self.chain = new_chain
    
        #旧链回放，这个不是真实的做法，但是因为我们没有状态树，区块少，所以这样很方便。
        new_balances = self.genesis_balances.copy()
    
        for block in self.chain:
            for tx in block.transactions:
                sender = tx["from"]
                receiver = tx["to"]
                amount = tx["amount"]
    
                if sender not in new_balances and sender != "COINBASE":
                    new_balances[sender] = 0
                if receiver not in new_balances:
                    new_balances[receiver] = 0
                
                #COINBASE奖励，直接给矿工加钱
                if sender == "COINBASE":
                    new_balances[receiver] += amount
                    continue
    
                #检查余额足够才应用
                if new_balances[sender] >= amount:
                    new_balances[sender] -= amount
                    new_balances[receiver] += amount
                
                #如果余额不足则跳过
                else:
                    continue
    
        #回写新的账户状态
        self.balances = new_balances
    
        print("Chain replaced successfully.")
        return True
#################################################################### 
#########################Fork + LCR截止于此#########################
####################################################################   


    def mine_block(self, miner_address="Miner", max_tx_per_block=5):
        """
        高层API，面向用户/矿工提供。给它一组交易，它会做什么呢：
        1. 构造区块。
        2. 进行PoW。
        3. 校验。
        4. 将挖好的区块加入链上。
        5. 返回新的区块。
        相当于区块链的大门入口吧。然后这里因为mempool的加入，从mempool自动打包交易，然后挖出新区快，还要筛选合法交易。
        其中max_tx_per_block我设定的是默认单个区块最多打包5个交易。
        """
        if len(self.mempool) == 0:
            print("Mempool empty. No transactions to mine.")
            return None
        
        tx_to_mine = [tx for tx in self.mempool[:max_tx_per_block]
                      if self.is_valid_transaction(tx)]
        
        reward_tx = {
            "from": "COINBASE",
            "to": miner_address,
            "amount": self.block_reward
        }
        tx_block = [reward_tx] + tx_to_mine #必须放在区块的第一个交易。
        
        new_block = Block(
            index=self.last_block.index + 1,
            transactions=tx_block,
            previous_hash=self.last_block.hash
        )
    
        print(f"Mining block {new_block.index} with difficulty {self.difficulty}")
        
        proof, mining_time = self.proof_of_work(new_block)
        
        #给区块记录真实完成时间
        new_block.mining_time = mining_time
        new_block.finish_time = time.time() + mining_time
        
        #现在不立即加入链，而是让 main 程序根据 finish_time 判断谁先挖到
        return new_block, proof
        
        #从mempool删除已打包交易
        self.mempool = self.mempool[max_tx_per_block:]        
        
        return new_block
    

    
    
    
    def __repr__(self):
        return f"Blockchain(length={len(self.chain)})"
