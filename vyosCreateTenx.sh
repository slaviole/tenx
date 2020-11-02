mytenx create classifier 10
mytenx create classifier 20 
mytenx create sfs vyos 2 4096 vnet-0 vnet-1
mytenx start sfs vyos
mytenx create sffs vpws 10 1 vnet-0
mytenx create sffs vpws 20 2 vnet-1

