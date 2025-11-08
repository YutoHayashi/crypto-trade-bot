from typing import List
import asyncio

from dependency_injector.wiring import inject, Provide

from batch_tasks.batch_task import BatchTask
from .logger import Logger


class Batch:
    max_count: int = 3600  # 1 hour
    count: int = 0
    tasks: List[BatchTask]
    
    async def run(self):
        """
        Start the batch service.
        This method starts the event loop and runs the tasks at the specified interval.
        """
        self.logger.system.info("The batch service is started.")
        while True:
            self.count += 1
            if self.count > self.max_count:
                self.count = 1
            
            if not self.paused:
                await asyncio.gather(
                    *[task() for task in self.tasks if (task.interval != 0) and (self.count % task.interval == 0)],
                    asyncio.sleep(1)
                )
            else:
                await asyncio.sleep(1)
    
    def pause(self):
        """
        Pause all tasks in the batch service.
        This method pauses all tasks that are currently running in the batch service.
        """
        self.paused = True
        self.logger.system.info("The batch service is paused.")
    
    def resume(self):
        """
        Resume all tasks in the batch service.
        This method resumes all tasks that have been paused.
        """
        self.paused = False
        self.logger.system.info("The batch service is resumed.")
    
    @inject
    def __init__(self,
                 tasks: List[BatchTask],
                 logger: Logger = Provide['logger']):
        """
        Initialize the Batch service with a list of tasks.
        :param tasks: A list of asynchronous tasks to run at the specified interval.
        :param logger: The logger service to log messages.
        """
        self.tasks = tasks
        self.logger = logger
        self.paused = False