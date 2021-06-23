from eth.vm.forks.petersburg.headers import (
    compute_difficulty,
)
from eth.vm.forks.berlin.headers import (
    configure_header,
    create_header_from_parent,
)


compute_simple_difficulty = compute_difficulty(9000000)

create_simple_header_from_parent = create_header_from_parent(
    compute_simple_difficulty
)
configure_simple_header = configure_header(compute_simple_difficulty)
