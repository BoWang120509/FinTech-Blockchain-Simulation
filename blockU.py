import time
import hashlib
import json

#这个部分是block，自然而然是作为咱这个项目核心存在，因此在模块化的时候我会把它放到第一位。
#具体block是啥我就不赘述了，咱这个block类属于是展示使用，算是极简版，省略了merkle tree,receipt,EVM,gas之类的内容。
#所以，实现的是正常学术模型的最小区块结构。
class Block:
    def __init__(self, index, transactions, previous_hash, timestamp=None, nonce=0):
        """
        那么这样一个最简区块结构都包含了什么：
        首先是index: 区块高度，也就是在链上的位置，目的是排序和显示。直接影响fork resolution
        然后是transactions: 交易列表，简化成了一个list，每个元素都是一个简单的交易。注意，这是简化版，没有引入gas消耗，调用合约，转账。
        第三是previous_hash: 链接上一个区块的哈希，修改前一个区块它的hash会变，后面的就都错了，所以是为了保证不变性。
        第四个是timestamp: 时间戳，也是简化版，没有使用矿工决定时间戳的真实做法。
        第五个是nonce: PoW使用的随机数。PoW的核心就是hash(block+nonce) < difficulty target。所以nonce的作用就是遍历，猜解。后面可能会频繁修改。
        第六个是tx_count: 是交易数的记录，主要为了debug的时候打印区块信息更清楚一点。
        第七个是block_size: 估计大小的作用。真实ETH里面这个东西不是固定的，主要根据gas limit和难度决定大小，咱们这个是简化版本，主要作为LCR和fork性能展示用。
        最后就是hash: 当前区块的哈希。一个作用是对外展示结果，再有一个就是让区块链记录最后hash。写入has的逻辑会在PoW完成。
        """
        self.index = index
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.tx_count = len(transactions)
        self.block_size = len(json.dumps(transactions))
        self.hash = None  #初始化为 None
        self.merkle_root = None #注意哦，这个只是单独保留一个占位字段，真实区块链用Merkle Tree，但这里就放一个placeholder来展示就好了。

    def compute_hash(self):
        """
        这个部分关键的很。
        首先是它给予了区块身份的证明，也就是说任何字段变化都会导致hash不同。
        其次它是作为PoW的基础，PoW就是反复修改nounce重复compute hash知道满足难度条件。
        再者就是为了给LCR打基础。如果hash错了，链就断了，那么最长链也自然不存在了。
        使用JSON而不适用dict主要是因为保证顺序，稳定并确定hash唯一性，永远序列化为同一个字符串。
        """
        block_string = json.dumps({
            "index": self.index,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "timestamp": self.timestamp,
            "nonce": self.nonce
        }, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()

    def __repr__(self):
        return f"Block(index={self.index}, hash={self.hash}, prev={self.previous_hash}, txs={len(self.transactions)})"

#总而言之，这个是后面所有内容的基础。
#在PoW中，会修改nounce，调整compute_hash()，对比difficulty，找到有效hash
#在LCR中，会寻找父节点，判断链长。
#在Account Model中，会用于更新全局账户状态。
#演示里面会进行block复制，构造分叉。