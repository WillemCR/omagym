require 'minitest'
require 'json'
module OmagymResults
  def run
    result = super
    puts "OMAGYM_RESULT #{JSON.generate(name: result.name, action: result.skipped? ? 'skip' : result.passed? ? 'pass' : 'fail')}"
    result
  end
end
Minitest::Test.prepend(OmagymResults)
