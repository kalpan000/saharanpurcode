#soething
from django.db import connection
from dateutil.relativedelta import relativedelta
from .models import ApplianceDataCollection
from psqlextra.partitioning import PostgresPartitioningManager,PostgresCurrentTimePartitioningStrategy,PostgresTimePartitionSize,partition_by_current_time,PostgresPartitioningConfig

manager = PostgresPartitioningManager([
    PostgresPartitioningConfig(
        model=ApplianceDataCollection,
        strategy=PostgresCurrentTimePartitioningStrategy(
            size=PostgresTimePartitionSize(months=1),
            count=10,
        ),
    ),
])

# these are the default arguments
partitioning_plan = manager.plan(
    skip_create=False,
    skip_delete=False,
    using='default'
)

# prints a list of partitions to be created/deleted
partitioning_plan.print()

# apply the plan
partitioning_plan.apply(using='default')