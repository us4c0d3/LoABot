import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
import tokens
import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from discord import ButtonStyle
import datetime
import pytz
import requests
import json
import asyncio
import math

apiurl = "https://developer-lostark.game.onstove.com/"
key = tokens.apikey

class Ssal(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @app_commands.command(name="분배금", description="경매 입찰 적정가 계산기")
    async def qqr(self, interaction: discord.Interaction, 가격: int) -> None:
        embed = self.auctioncalc(가격)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="전설지도", description="전설지도 입찰 적정가 계산기")
    async def legendaryMap(self, interaction: discord.Interaction) -> None:
        voldaik = Button(label='볼다이크', style=ButtonStyle.primary)
        bern = Button(label='베른 남부', style=ButtonStyle.primary)

        async def voldaik_callback(interaction: discord.Interaction):
            embed = self.legendaryMap_Voldaik()
            await interaction.response.send_message(embed=embed)

        async def bern_callback(interaction: discord.Interaction):
            embed = self.legendaryMap_Bern()
            await interaction.response.send_message(embed=embed)

        voldaik.callback = voldaik_callback
        bern.callback = bern_callback

        view = View()
        view.add_item(voldaik)
        view.add_item(bern)
        await interaction.response.send_message("지역을 선택해주세요. 이 메시지는 5초 후 삭제됩니다.", view=view, delete_after=5)


    '''
    16인 레이드 추가될 시 주석 해제
    '''
    def auctioncalc(self, common_price: int):
        if common_price >= 100000:
            common_price = int(common_price * 0.95)
        price = []
        fair4 = math.floor(common_price * 0.95 * 3/4)
        fair8 = math.floor(common_price * 0.95 * 7/8)
        # fair16 = math.floor(common_price * 0.95 * 3/4)
        fairfield = math.floor(common_price * 0.95 * 29/30)

        price.append(fair4)
        price.append(fair8)
        price.append(fairfield)

        fair = []
        for i in range(3):
            fair.append(math.floor(price[i]/1.1))

        
        embed = discord.Embed(title=":scales: 경매 입찰 적정가 계산기", description=f"[:coin:`{common_price}`]", timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.add_field(name="손익분기점", value=f"4인: [:coin:`{price[0]}`]\n8인: [:coin:`{price[1]}`]", inline=False)
        embed.add_field(name="적정입찰가", value=f"4인: [:coin:`{fair[0]}`]\n8인: [:coin:`{fair[1]}`]", inline=False)
        embed.add_field(name="분배금", value=f"4인: [:coin:`{math.floor(fair[0] * 1/3)}`]\n8인: [:coin:`{math.floor(fair[1] * 1/7)}`]", inline=False)
        embed.add_field(name="필보입찰가", value=f"[:coin:`{price[2]}`]", inline=False)
        embed.set_footer(text="Made by 우사니#3136")
        return embed


    # 볼다이크
    def legendaryMap_Voldaik(self):
        '''
        은축가 각각 16, 8, 4개 solar grace, blessing, protection (최소 개수 기준, 축복 최대 12개)
        명파주머니(대) 8개 honor shard pouch(최소 개수 기준, 최대 12개)
        3티어 1레벨 보석 48개
        '''
        self.gem_price = self.get_gem_price()
        self.overall_gem_price = self.gem_price * 48

        self.solar_price = self.get_solar_price()
        self.overall_solar_price = {}
        j = 12
        for i in self.solar_price:
            self.overall_solar_price[i] = self.solar_price[i] * j
            j -= 4
        self.overall_solar_price['태양의 은총'] += self.solar_price['태양의 은총'] * 4

        self.honor_price = self.get_honor_price()
        self.overall_honor_price = self.honor_price * 8
        
        # print(self.overall_gem_price, self.overall_solar_price, self.overall_honor_price)

        self.price = 0
        for i in self.overall_solar_price:
            self.price += self.overall_solar_price[i]
        self.price += self.overall_gem_price
        self.price += self.overall_honor_price

        return self.makeEmbed('볼다이크')


    # 베른 남부
    def legendaryMap_Bern(self):
        '''
        은축가 각각 12, 8, 4개 solar grace, blessing, protection
        명파주머니(대) 8개 honor shard pouch
        3티어 1레벨 보석 40개
        '''
        self.gem_price = self.get_gem_price()
        self.overall_gem_price = self.gem_price * 40

        self.solar_price = self.get_solar_price()
        self.overall_solar_price = {}
        j = 12
        for i in self.solar_price:
            self.overall_solar_price[i] = self.solar_price[i] * j
            j -= 4

        self.honor_price = self.get_honor_price()
        self.overall_honor_price = self.honor_price * 8
        
        # print(self.overall_gem_price, self.overall_solar_price, self.overall_honor_price)

        self.price = 0
        for i in self.overall_solar_price:
            self.price += self.overall_solar_price[i]
        self.price += self.overall_gem_price
        self.price += self.overall_honor_price

        # print(price)
        return self.makeEmbed('베른 남부')


    def makeEmbed(self, name: str):
        self.price_message = self.price_format()
        self.honor_message = self.message_format(self.honor_price, self.overall_honor_price)
        self.gem_message = self.message_format(self.gem_price, self.overall_gem_price)

        embed=discord.Embed(title=f":moneybag: {name} 전설지도 입찰 적정가 계산기", description=self.price_message, timestamp=datetime.datetime.now(pytz.timezone('UTC')))
        embed.add_field(name="명예의 파편 주머니(대)", value=self.honor_message, inline=False)
        embed.add_field(name="3티어 1레벨 보석", value=self.gem_message, inline=False)
        # print(price_message)
        # print(honor_message)
        # print(gem_message)
        for i in self.solar_price:
            message = self.message_format(self.solar_price[i], self.overall_solar_price[i])
            # print(message)
            embed.add_field(name=i, value=message, inline=True)
        embed.set_footer(text="Made by 우사니#3136")

        return embed


    def price_format(self):
        fairprice = math.floor(self.price * 0.95 * 29/30)
        distprice = math.floor(fairprice * 1/29)
        message = [
            f"가격: :coin:`{self.price}`",
            f"손익분기점: :coin:`{fairprice}`",
            f"적정입찰가: :coin:`{math.floor(fairprice/1.1)}`",
            f"분배금: :coin:`{distprice}`"
        ]
        return '\n'.join(message)


    def message_format(self, price: int, overall_price: int):
        message = [
            f"시세: :coin:`{price}`",
            f"합계: :coin:`{overall_price}`"
        ]

        return '\n'.join(message)


    def get_gem_price(self):
        url = apiurl + "auctions/items/"
        headers = {'accept': 'application/json', 'authorization': 'bearer ' + key, 'Content-Type': 'application/json'} 
        data = {
            "ItemLevelMin": 0,
            "ItemLevelMax": 1700,
            "ItemGradeQuality": 0,
            "Sort": "BUY_PRICE",
            "CategoryCode": 210000,
            "CharacterClass": "",
            "ItemTier": 3,
            "ItemGrade": "",
            "ItemName": "",
            "PageNo": 1,
            "SortCondition": "ASC"
        }
        try:
            response = requests.post(url, json=data, headers=headers).json()
            # print(response.text)
            # with open("result.json", 'w', encoding='utf-8') as f:
            #     json.dump(response.json(), f, ensure_ascii=False, indent='\t')

            index = 0
            sum = 0
            for item in response['Items']:
                index = index + 1
                if index == 5 or index == 6:
                    sum += item['AuctionInfo']['BuyPrice']
                if index == 6: break
            
            sum = math.floor(sum/2)
            
            # print(sum)
            return sum

        except Exception as e:
            print(e)
            return -1


    def get_solar_price(self):
        url = apiurl + 'markets/items/'
        data = {
            "Sort": "GRADE",
            "CategoryCode": 50020,
            "ItemTier":3,
            "ItemGrade": "",
            "ItemName": "태양의",
            "PageNo": 1,
            "SortCondition": "ASC"
        }
        headers = {'accept': 'application/json', 'authorization': 'bearer ' + key, 'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=data, headers=headers).json()
            # print(response)
            solar = {}
            for item in response['Items']:
                solar[item['Name']] = item['CurrentMinPrice']

            # print(sum)
            return solar       

        except Exception as e:
            print(e)
            return -1



    def get_honor_price(self):
        url = apiurl + 'markets/items/'
        data = {
            "Sort": "GRADE",
            "CategoryCode": 50010,
            "ItemTier": 3,
            "ItemGrade": "",
            "ItemName": "명예의 파편 주머니(대)",
            "PageNo": 1,
            "SortCondition": "ASC"
        }
        headers = {'accept': 'application/json', 'authorization': 'bearer ' + key, 'Content-Type': 'application/json'}

        try:
            response = requests.post(url, json=data, headers=headers).json()
            # print(response)
            return response['Items'][0]['CurrentMinPrice']

        except Exception as e:
            print(e)
            return -1

async def setup(bot) -> None:
    # await bot.add_cog(Ssal(bot), guilds=[discord.Object(id=tokens.guild_id)])
    await bot.add_cog(Ssal(bot))