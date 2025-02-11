const SHA256= require('crypto-js/sha256');

class Block{
    constructor(index, timestamp, data, previousHash = ''){
        this.index=index;
        this.timestamp= timestamp;
        this.data= data;
        this.previousHash= previousHash
        this.hash= this.calcHash();
    }

    calcHash(){
        //Function to calculate the hash of the block
       return SHA256(this.index + this.previousHash + this.timestamp + JSON.stringify(this.data)).toString(); 
    }
}

class Blockchain{
    constructor(){
        this.chain= [this.createGenesis()];
    }

    createGenesis(){
        //Creating our first block called Genesis manually
        return new Block(0, "2/8/2025", "Genesis Block", "0");
    }

    getLastBlock(){
        return this.chain[this.chain.length-1]
    }

    addNewBlock(newBlock){
        newBlock.previousHash= this.getLastBlock().hash;
        newBlock.hash= newBlock.calcHash(); // Calculating a hash for the new block
        this.chain.push(newBlock);
   }

    isChainValid(){
        //Function to check the validity of the block
        for(let i=1; i< this.chain.length; i++){
            const currentBlock= this.chain[i];
            const previosuBlock= this.chain[i -1];
            if(currentBlock.hash != currentBlock.calcHash()){
                return false;
            }
            if(currentBlock.previousHash != previosuBlock.hash){
                return false;
            }
        }
        return true;
    }
}

let blockchain= new Blockchain(); //Create instance of blockchain
blockchain.addNewBlock(new Block(1, "2025-02-10T00:00:00Z", {block1: "Alice paid Bob 100$"}));
blockchain.addNewBlock(new Block(2, "2025-02-10T14:00:00Z", {block2: "Bob paid Charlie 100$"}));
blockchain.addNewBlock(new Block(3, "2025-02-11T01:00:00.000Z", {block2: "Bob paid Jack 50$"}));

console.log(JSON.stringify(blockchain, null, 4)) 
console.log('Is blockchain valid?' + blockchain.isChainValid()); //Check if the blockchain is valid before tampering with

blockchain.chain[1].data= {block1:"Alice paid Bob 55$"} ; //Tamper with block 1
blockchain.chain[1].hash= blockchain.chain[1].calcHash(); //Recalculate the hash of block 1

console.log("New hash of Block 1: " + blockchain.chain[1].hash);
console.log('Is blockchain valid?' + blockchain.isChainValid()); //Check if the blockchain is valid after tampering with

