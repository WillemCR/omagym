require 'active_record'
class Book < ActiveRecord::Base
  def self.available
    raise NotImplementedError, 'Return the available catalogue relation'
  end
  def self.priced_between(_minimum, _maximum)
    raise NotImplementedError, 'Return the price range relation'
  end
end
