# -*- coding: utf-8 -*-
import lib601.search as search
import lib601.sm as sm

# Indices into the state tuple.
(farmer, goat, wolf, cabbage) = 0,1,2,3


class FarmerGoatWolfCabbage(sm.SM):
    startState = ('L', 'L', 'L', 'L')
    legalInputs = ['takeGoat', 'takeWolf', 'takeCabbage', 'takeNone']

    def getNextValues(self, state, action):
        nextState = list(state)

        # 计算农夫下一步的位置
        farmer_position = state[farmer]
        next_side = 'R' if farmer_position == 'L' else 'L'

        # 如果要带物品，物品必须在农夫同侧
        if (action == 'takeGoat' and state[farmer] != state[goat]) or (action == 'takeWolf' and state[farmer] != state[wolf]) or (action == 'takeCabbage' and state[farmer] != state[cabbage]):
            return (state, state)

        # 农夫移动到对岸
        nextState[farmer] = next_side

        if action == 'takeGoat':
            nextState[goat] = next_side
        elif action == 'takeWolf':
            nextState[wolf] = next_side
        elif action == 'takeCabbage':
            nextState[cabbage] = next_side

        # 羊和白菜不能单独在一起，羊和狼不能单独在一起
        if nextState[goat] == nextState[wolf] and nextState[farmer] != nextState[goat]:
            return (state, state)

        # 羊和白菜在相同岸边，但农夫不在该岸边
        if nextState[goat] == nextState[cabbage] and nextState[farmer] != nextState[goat]:
            return (state, state)

        return (tuple(nextState), tuple(nextState))

    def done(self, state):
        # 所有人都在右岸
        return state == ('R', 'R', 'R', 'R')

solution = FarmerGoatWolfCabbage()
solution_path = search.smSearch(solution)

print("Solution found (sequence of actions):")
if solution_path:
    for action in solution_path:
        print("- %s" % (action,))
else:
    print("No solution found.")