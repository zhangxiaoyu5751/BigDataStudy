# -*- coding: utf-8 -*-
# python代码各种排序 升序排列
class SortMethod(object):

    def __init__(self):
        pass
    
    # 冒泡排序 时间复杂度o(n2)  是稳定排序
    # 冒泡排序的思想是，通过一次遍历，对相邻数据进行大小的两两比较，然后选出整行最大的数据，第二次遍历选出第二大的数据。
    def bubble_sort(self, data_list):
        for i in range(len(data_list)-1):
            for j in range(len(data_list) - 1 - i):
                if data_list[j] > data_list[j + 1]:
                    data_list[j], data_list[j + 1] = data_list[j+1], data_list[j]
        return data_list
    
    # 插入排序 时间复杂度o(n2) 是稳定排序
    def insert_sort(self, data_list):
        for i in range(1, len(data_list)):
            temp = data_list[i]
            j = i -1
            while j >= 0 and temp < data_list[j]:
                data_list[j + 1] = data_list[j]
                j -= 1
            data_list[j+1] = temp
        return data_list

    # 选择排序 是不稳定的排序 时间复杂度o(n2)
    def select_sort(self, data_list):
        for i in range(len(data_list)-1):
            min_index = i 
            for j in range(i + 1, len(data_list)):
                if data_list[i] > data_list[j]:
                    min_index = j
            data_list[i], data_list[min_index] = data_list[min_index], data_list[i]
        return data_list
        

    # 归并排序 o(nlogn)
    def merge_sort(self, data_list):
        if len(data_list) == 1 or len(data_list) == 0:
            return data_list
        
        mid = len(data_list) / 2

        left = self.merge_sort(data_list[:mid])
        right = self.merge_sort(data_list[mid:])
        result = self.partition_sort(left, right)
        return result

    @staticmethod
    def partition_sort(left, right):
        result = []
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        result += left[i:]
        result += right[j:]
        return result

    # 快排O(nlogn)
    def quick_sort(self, data_list, left, right):
        if left >= right:
            return 
        low = left
        high = right
        temp = data_list[low]
        while low < high:
            while low < high and data_list[high] >= temp:
                high -= 1
            data_list[low] = data_list[high]

            while low < high and data_list[low] < temp:
                low = low + 1
            data_list[high] = data_list[low]

        data_list[low] = temp
        self.quick_sort(data_list, left, low)
        self.quick_sort(data_list, low+1, right)






    
    # 二分查找
    def binary_search(self, data_list, num):
        data_list.sort()
        left = 0
        right = len(data_list) - 1 
        while left <= right:
            mid = (right + left) / 2
            if data_list[mid] < num:
                left = mid + 1
            elif data_list[mid] > num:
                right = mid - 1
            else:
                return mid
        return -1


    # 堆排序O(nlogn) 不稳定
    



if __name__ == "__main__":
    a = SortMethod()
    b = [123,1235,2346,37,12,3123,123,235,2356]
    print a.binary_search(b, 999999)
