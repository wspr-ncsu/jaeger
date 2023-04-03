from json import loads
from pathlib import Path

class TelcoIndustry:
    __total_subscribers_count = 0
    
    def __init__(self) -> None:
        stream = open(f'{Path.cwd()}/cdrs/telcos.json')
        self.carriers = loads(stream.read())
        self.get_total_subscribers()
        
    def get_total_subscribers(self):
        if (self.__total_subscribers_count > 0):
            return self.__total_subscribers_count
        
        index = 0
        key = 'no_of_subscribers'
        
        while index < len(self.carriers):
            subscribers = int(self.carriers[index].get(key) * pow(10, 6))
            self.carriers[index][key] = subscribers
            self.__total_subscribers_count += subscribers
            index += 1
            
        return self.__total_subscribers_count
    
    def get_prob_different_networks_call(self):
        summation = 0
        key = 'no_of_subscribers'
        
        for carrier in self.carriers:
            no_of_subscribers = carrier.get(key)
            summation += pow(no_of_subscribers, 2) - no_of_subscribers
        
        factor = 1 / (pow(self.__total_subscribers_count, 2) - self.__total_subscribers_count)
        
        prob_same_net_call = factor * summation
        
        return 1 - prob_same_net_call


if __name__ == '__main__':
    industry = TelcoIndustry()
    prob = industry.get_prob_different_networks_call()
    print(f"Probability of different network call = {prob}")