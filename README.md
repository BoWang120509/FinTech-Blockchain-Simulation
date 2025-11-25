# FinTech-Blockchain-Simulation
Python Blockchain Simulation (PoW + Mempool + LCR + Fork + Double-Spend)
This repository implements a fully custom blockchain simulation in Python, designed to demonstrate the internal mechanics of modern Proof-of-Work (PoW) blockchains such as Bitcoin and Ethereum (PoW era).
This project was developed for a graduate-level FinTech course.

--Features Implemented
This project includes full implementations of the core blockchain mechanisms:
1. Block Structure (block.py)
-Index
-Transaction list
-Nonce
-Previous hash
-SHA-256 hash calculation
This module defines the fundamental unit of the blockchain.

2. Blockchain System (blockchain.py)
A full blockchain simulation including:
-Proof-of-Work (PoW)
-Mempool (Pending Transactions Pool)
-Account-Based Model
-Miner Rewards (Coinbase Transaction)
-Fork Simulation
-Longest Chain Rule (LCR)
-Double-Spend Demonstration

--Running the Simulation
Simply run the main file, You will see:
1. Normal chain operation
2. Fork creation
3. Competing miners
4. Chain comparison
5. Reorganization
6. Double-spend result
7. Final balances
8. Final chain structure

--What This Project Demonstrates
This project is a complete teaching-level blockchain simulation, covering:
-Blockchain Consensus
1. PoW difficulty
2. Hash grinding
3. Nonce search
4. Valid block linking
-State Transition System
1. Apply transactions sequentially
2. Enforce no-negative-balance rule
3. Recompute state after chain reorg
-Chain Security
1. How forks happen
2. Why LCR resolves them
3. How a double-spend attack works
4. How attack success modifies final state
-Economic Model
1. Coinbase reward issuance
2. Supply growth through block rewards
3. How a miner accumulates wealth

--Academic Purpose
This project was developed for:
1. Graduate-level FinTech blockchain coursework
2. Demonstration of blockchain internal logic
3. Explanation of consensus, mempool, and reorg events
4. Double-spend attack educational simulation
It is not intended to run on a real network or maintain long-term state security.
It is an educational model showcasing core blockchain principles.

--Next Steps (Optional Enhancements)
If extended in the future, possible upgrades include:
1. Transaction fees (gas)
2. More realistic mempool selection (priority fees)
3. Network propagation delay
4. Realistic attacker with hash-power fraction p
5. State trie (Merkle Patricia Tree)
6. Parallel miners / threading









