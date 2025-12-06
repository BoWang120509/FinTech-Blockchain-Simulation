from blockU import Block
from blockCU import Blockchain
import copy
import matplotlib.pyplot as plt
import time
#这个是主文件

##### Block部分测试 #####
#注意噢，我手动设置了index=0是因为这个区块是“测试用创世区块”，和普通创世区块一样没有parent，全0占位。
#还有一个点，我在blockchain，也就是第二个模块里面直接引用了block，也就是第一模块，所以这个测试部分可以不必调用。
b = Block(index=0, transactions=["tx1", "tx2"], previous_hash="0"*64)

print("\n==================== BLOCK UNIT TEST ====================\n")
print("==THIS IS THE TEST PART, NOT EMBEDDED IN THE MAIN FRAME==\n")
print("Block created:")
print("Index:", b.index)
print("Transactions:", b.transactions)
print("Previous Hash:", b.previous_hash)

print("\nComputing hash...")
h = b.compute_hash()
print("Hash:", h)


def print_chain(chain):
    print()
    for b in chain:
        print(f"Block #{b.index} | Hash={b.hash[:12]}... | TXs={len(b.transactions)}")
    print()


def extract_transactions(chain):
    txs = []
    for b in chain:
        for tx in b.transactions:
            if tx["from"] != "COINBASE":
                txs.append(tx)
    return txs


##### BlockChain+PoW部分 #####
#整个使用流程大概是：
#1. 用户发送交易 --> 2. 交易进入mempool --> 3. 矿工打包 --> 4. 校验合法hash --> 5. 区块入链 --> 6. 交易状态更新 --> 7. 账户余额更新。
#初始化链
bc = Blockchain(difficulty=4)
print("\n==================== PART 1: NORMAL BLOCKCHAIN COMPUTING ====================\n")
print("After creating genesis block:")
print(bc.chain)

#添加交易进入Mempool。
#后面的交易额直接与初始账户余额和后续账户余额挂钩，可以更改。
print("\nAdding transactions...")
bc.add_transaction("AAAAA", "BBBBB", 5)
bc.add_transaction("BBBBB", "CCCCC", 3)
bc.add_transaction("CCCCC", "DDDDD", 2)

#使用PoW开挖区块，自动从mempool打包交易
print("\nMining block #1")
block1 = bc.mine_block()
#再添加一些交易
bc.add_transaction("DDDDD" , "EEEEE", 1)
bc.add_transaction("EEEEE" , "AAAAA", 10)

print("\nMining block #2")
block2 =bc.mine_block()

#显示最终链结构
print("\n==================== PART 1: FINAL NORMAL BLOCKCHAIN ====================\n")
for blk in bc.chain:
    print(blk)

print("\nRemaining mempool:")
print(bc.mempool)


#####基于Blockchain部分下的分叉/LCR/双花演示#####
print("\n\n==================== PART 2: FORK + LCR + REORG DEMO ====================\n")
honest = Blockchain(difficulty=3,miner_hashrate=1)
attacker = Blockchain(difficulty=3,miner_hashrate=1)


#攻击者复制honest的创世状态
attacker.chain = copy.deepcopy(honest.chain)
attacker.balances = copy.deepcopy(honest.balances)

print("Honest TX: AAAAA --> BBBBB (10)")
honest.add_transaction("AAAAA", "BBBBB", 10)

print("Attacker TX: AAAAA --> AttackerWallet (10)")
attacker.add_transaction("AAAAA", "AttackerWallet", 10)

print("\n--- Both sides mine block #1 ---")
h_blk, h_proof = honest.mine_block(miner_address="HonestMiner")
a_blk, a_proof = attacker.mine_block(miner_address="AttackerMiner")

#判断谁更快
if h_blk.finish_time < a_blk.finish_time:
    honest.add_block(h_blk, h_proof)
    print("Honest miner found block first.")
else:
    attacker.add_block(a_blk, a_proof)
    print("Attacker miner found block first.")


#这部分是限定时间内，诚实的人和攻击者一起挖矿，谁先挖到算谁的。
#具体参见白皮书第四部分，也就是说到的区块产生时间服从指数分布。链的增长服从赌徒随机游走模型。
end_time = time.time() + 30#模拟 30 秒

while time.time() < end_time:
    #honest 尝试挖一个区块
    h_blk, h_proof = honest.mine_block("HonestMiner")

    #attacker 尝试挖一个区块
    a_blk, a_proof = attacker.mine_block("AttackerMiner")

    #谁先挖到就加入谁的链
    if h_blk.finish_time < a_blk.finish_time:
        honest.add_block(h_blk, h_proof)
        print("Honest mined a block")
    else:
        attacker.add_block(a_blk, a_proof)
        print("Attacker mined a block")


print("\n=== CHAIN LENGTH COMPARISON ===")
print("Honest:", len(honest.chain))
print("Attacker:", len(attacker.chain))

if len(attacker.chain) > len(honest.chain):
    print("\nAttacker wins. Reorganizing honest chain")

    honest_chain_before_reorg = honest.chain.copy()
    attacker_chain_before_reorg = attacker.chain.copy()

    honest.replace_chain(attacker.chain)
else:
    honest_chain_before_reorg = honest.chain.copy()
    attacker_chain_before_reorg = attacker.chain.copy()

print("\n=== FINAL BALANCES AFTER REORG ===")
print(honest.balances)

print("\n=== FINAL CHAIN ===")
print_chain(honest.chain)




honest_times = [blk.mining_time for blk in honest_chain_before_reorg[1:]]
attacker_times = [blk.mining_time for blk in attacker_chain_before_reorg[1:]]


plt.figure(figsize=(12,6))

#Honest miner: x = 1,2,3,...len(honest_times)
plt.plot(range(len(honest_times)), honest_times, label="Honest Mining Time")

#Attacker miner: x = 1,2,3,...len(attacker_times)
plt.plot(range(len(attacker_times)), attacker_times, label="Attacker Mining Time")

plt.xlabel("Block Index Within Each Chain")
plt.ylabel("Mining Time (seconds)")
plt.title("Mining Time Comparison (Honest vs Attacker)")
plt.legend()
plt.grid(True)
plt.show()

