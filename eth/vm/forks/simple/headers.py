from eth.vm.forks.berlin.headers import (
    configure_header,
    create_header_from_parent,
    compute_berlin_difficulty,
)


compute_simple_difficulty = compute_berlin_difficulty

create_simple_header_from_parent = create_header_from_parent(
    compute_simple_difficulty
)
configure_simple_header = configure_header(compute_simple_difficulty)
