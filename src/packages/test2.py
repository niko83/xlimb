import xlimb_helper

if __debug__ is not True:
    raise("Check __debug__ option")

assert xlimb_helper.distance((1,1), (2,2)) == 1.4142135623730951
print('OK distance')
assert xlimb_helper.resolve_line((0,0), (2,2)) == (1.0, 1.0)
print('OK resolve_line')
assert xlimb_helper.get_polygon_idx_collision(100.0, 1500.0) == 13
print('OK get_polygon_idx_collision')


#  class Vector():
    #  def __init__(self):
        #  self.x = 100
        #  self.y = 200

#  class A(object):
    #  def __init__(self, x):
        #  self.life_limit=100
        #  self.able_to_make_tracing=2
        #  self.current_speed=Vector()
        #  self.current_position=Vector()
        #  self.approx_x=60
        #  self.approx_y=60
        #  self.ricochet = 1

#  a = A(111)
#  xlimb_helper.calculate_position(0.002, a)

#  print(a.life_limit)
#  print(a.able_to_make_tracing)
#  print(a.current_speed.x)
#  print(a.current_speed.y)
#  print(a.current_position.x)
#  print(a.current_position.y)
#  print(a.approx_x)
#  print(a.approx_y)
#  print(a.ricochet)
