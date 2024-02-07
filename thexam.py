import pandas as pd


class Token:

    def __init__(self, initial_supply=21e9, emission_rate=0.05, annual_emission_cap=0.04, treasury_allocation=0.1):

        self.total_supply = initial_supply

        self.emission_rate = emission_rate

        self.annual_emission_cap = annual_emission_cap

        self.treasury_allocation = treasury_allocation

        self.treasury_balance = initial_supply * treasury_allocation  

        self.value = 1  


    def apply_emission(self, validators):

        emission_amount = min(self.total_supply * self.emission_rate, self.total_supply * self.annual_emission_cap)

        treasury_emission = emission_amount * self.treasury_allocation

        validator_incentives = emission_amount * 0.1  # Assuming 10% of emissions go to validators

        self.treasury_balance += treasury_emission

        self.distribute_validator_incentives(validator_incentives, validators)

        self.total_supply += (emission_amount - treasury_emission - validator_incentives)

        self.recalculate_value()  


    def distribute_validator_incentives(self, incentives, validators):

        incentive_per_validator = incentives / len(validators)

        for validator in validators:

            validator.reward_balance += incentive_per_validator

            

    def recalculate_value(self):

        # Assuming token value is proportional to the ratio of treasury balance to total supply

        self.value = self.treasury_balance / self.total_supply


class Validator:

    def __init__(self, validator_id, operational_cost=10000):

        self.validator_id = validator_id

        self.operational_cost = operational_cost

        self.reward_balance = 0


    def validate_transaction(self, transaction):

        if transaction.fee >= transaction.min_fee:

            self.reward_balance += transaction.fee

            return True

        return False


class Wallet:

    def __init__(self, owner, balance=0):

        self.owner = owner

        self.balance = balance

        self.staked_balance = 0


class Transaction:

    def __init__(self, sender: Wallet, receiver: Wallet, amount, fee, min_fee=1):

        self.sender = sender

        self.receiver = receiver

        self.amount = amount

        self.fee = fee

        self.min_fee = min_fee


    def execute(self):

        if self.sender.balance >= (self.amount + self.fee) and self.fee >= self.min_fee:

            self.sender.balance -= (self.amount + self.fee)

            self.receiver.balance += self.amount

            return True

        return False


class StakingMechanism:

    def __init__(self, interest_rate=0.05, minimum_stake=1000):  # a minimum stake requirement

        self.interest_rate = interest_rate

        self.minimum_stake = minimum_stake


    def stake_tokens(self, wallet: Wallet, amount):

        if wallet.balance >= amount and amount >= self.minimum_stake:  

            wallet.balance -= amount

            wallet.staked_balance += amount * (1 + self.interest_rate)


    def unstake_tokens(self, wallet: Wallet, amount):

        if wallet.staked_balance >= amount:

            wallet.staked_balance -= amount

            wallet.balance += amount


class SimulationData:

    def __init__(self):

        self.data = pd.DataFrame(columns=['Time', 'TokenValue', 'TotalSupply', 'TreasuryBalance'])


    def log_data(self, time, token: Token):

        self.data = self.data.append({'Time': time, 'TokenValue': token.value, 'TotalSupply': token.total_supply, 'TreasuryBalance': token.treasury_balance}, ignore_index=True)


        

        

# Components to run the simulation

OHM = Token()

validators = [Validator(validator_id='Validator1'), Validator(validator_id='Validator2')]

wallet1 = Wallet("Alice", 100000)

wallet2 = Wallet("Bob", 100000)

staking = StakingMechanism(0.05, 1000)

data_logger = SimulationData()


# Simulate over 10 years

for year in range(1, 11): 

    OHM.apply_emission(validators)  # Apply emission annually

    

    

    if year == 1:

        staking.stake_tokens(wallet1, 50000)  


    # Random transaction

    transaction1 = Transaction(wallet1, wallet2, 1000, 10)

    if transaction1.execute():

        validators[0].validate_transaction(transaction1)  

    

    if year == 5:

        staking.unstake_tokens(wallet1, 25000)

    

    data_logger.log_data(year, OHM)  # Log data annually


print(data_logger.data)










## Dashboard

import dash

from dash import html, dcc, Input, Output, State

import pandas as pd

import plotly.express as px



def run_simulation(initial_supply, emission_rate, annual_emission_cap, treasury_allocation, years=10):

    token = Token(initial_supply, emission_rate, annual_emission_cap, treasury_allocation)

    validators = [Validator(validator_id='Validator1'), Validator(validator_id='Validator2')]

    wallet1 = Wallet("Alice", 100000)

    wallet2 = Wallet("Bob", 100000)

    staking = StakingMechanism(0.05, 1000)

    data_logger = SimulationData()


    for year in range(1, years + 1):

        token.apply_emission(validators)

        if year == 1:

            staking.stake_tokens(wallet1, 50000)

        data_logger.log_data(year, token)


    return data_logger.data


# Dash app setup

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Token Economy Simulation Dashboard"),

    html.Div([

        html.Label("Initial Supply:"),

        dcc.Input(id='initial-supply', type='number', value=21e9),

        html.Label("Emission Rate:"),

        dcc.Input(id='emission-rate', type='number', value=0.05),

        html.Label("Annual Emission Cap:"),

        dcc.Input(id='annual-emission-cap', type='number', value=0.04),

        html.Label("Treasury Allocation:"),

        dcc.Input(id='treasury-allocation', type='number', value=0.1),

    ]),

    html.Button('Run Simulation', id='run-simulation', n_clicks=0),

    dcc.Graph(id='simulation-graph')

])


@app.callback(

    Output('simulation-graph', 'figure'),

    Input('run-simulation', 'n_clicks'),

    State('initial-supply', 'value'),

    State('emission-rate', 'value'),

    State('annual-emission-cap', 'value'),

    State('treasury-allocation', 'value')

)

def update_graph(n_clicks, initial_supply, emission_rate, annual_emission_cap, treasury_allocation):

    if n_clicks > 0:

        data = run_simulation(initial_supply, emission_rate, annual_emission_cap, treasury_allocation)

        fig = px.line(data, x='Time', y=['TokenValue', 'TotalSupply', 'TreasuryBalance'], title="Token Economy Simulation Results")

        return fig

    else:

        return px.line(title="Simulation results will appear here")


if __name__ == '__main__':

    app.run_server(debug=True)

