
def HASH(object):
    def __init__(self):
        self.hashtable = [[None,None] for i in range(11)]

    def hash(str1):
        return str1
    def get_hash(self, k, v):
        index = (hash(k) + v) % len(self.hashtable)
        if self.hashtable[index][0] == k:
            return index
        if self.hashtable[index][0]:
            return self.get_hash(k, v+1)
    
    def put(self, k, v):
        index = self.get_hash(k, 0)
        self

if __name__ == "__main__":
    def longestConsecutive(nums):
            hash_dict = dict()
            
            max_length = 0
            for num in nums:
                if num not in hash_dict:
                    left = hash_dict.get(num - 1, 0)
                    right = hash_dict.get(num + 1, 0)
                    
                    cur_length = 1 + left + right
                    if cur_length > max_length:
                        max_length = cur_length
                    
                    hash_dict[num] = cur_length
                    hash_dict[num - left] = cur_length
                    hash_dict[num + right] = cur_length
            print hash_dict
            return max_length
    nums = [1,123,135,2,3,5,4]
    longestConsecutive(nums)




    


