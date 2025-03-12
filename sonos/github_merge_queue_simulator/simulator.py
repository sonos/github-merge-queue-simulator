#!/usr/bin/env python3

import random
import logging
import argparse
import statistics

logging.basicConfig(level=logging.INFO, format='  %(message)s')
logger = logging.getLogger(__name__)


def simulate_throughput(queue_size: int, sim_duration: int, job_duration: int, failure_probability: float,
                        jobs_waiting_to_enter: int = 0, jobs_waiting_to_enter_probability: float = 0) -> tuple:
    """Compute the throughput of a queue given various parameters.
    
    Args:
        queue_size (int): Number of jobs in the queue
        sim_duration (int): Duration of the simulation in minutes
        job_duration (int): Duration of each job in minutes
        failure_probability (float): Probability of a job failing expressed as a number between 0 and 1
        jobs_waiting_to_enter (int): Number of jobs waiting to enter the queue simulating a queue being full and
            number of jobs waiting to enter.  It works with 'jobs_waiting_to_enter_rate' setting, default: 0
        jobs_waiting_to_enter_probability (int): Probability of jobs waiting to enter the queue.  This setting determines
            how often there is an occurance of 'jobs_waiting_to_enter' waiting to enter the queue simulating
            queue being full and jobs waiting.  This setting is expressed as a number between 0 and 1, default: 0

    Returns:
        tuple: a tuple containing throughput of jobs per hour, jobs lost per hour, average time to merge in minutes,
            and median time to merge in minutes
    """
    total_jobs_completed = 0
    total_time = 0
    total_jobs_lost = 0
    
    # track a list of all wait times per iteration
    wait_times = []

    # run simulation
    while total_time < sim_duration:
        
        jobs_completed = 0

        # roll through the queue and pick a job to fail based on probability
        for _ in range(1, queue_size + 1):
            # if job failure occurs based on assigned probability
            if random.random() <= failure_probability:
                break
            
            # job completed OK
            else:
                jobs_completed += 1
        

        # track jobs completed and lost in this iteration
        total_jobs_completed += jobs_completed
        total_jobs_lost += queue_size - jobs_completed
        
        # increment by job execution time
        total_time += job_duration

        # can't divide by zero, this happens if the first jobs gets bounced and displaces all jobs, ignore that case
        if jobs_completed > 0:

            jobs_in_line = queue_size

            # if jobs are waiting to enter the queue based on assigned probability
            # add them to the total waiting line which will impact avearge wait time
            if random.random() <= jobs_waiting_to_enter_probability:
                jobs_in_line += jobs_waiting_to_enter

            # wait time is: jobs / rate of jobs completing
            # from Little's Law: https://en.wikipedia.org/wiki/Little%27s_law
            wait_times.append(jobs_in_line / (jobs_completed / job_duration))


    # compute throughput of jobs / hour
    throughput = round(total_jobs_completed / (total_time / 60), 1)

    # compute average number of jobs lost / hour
    jobs_lost_rate = round(total_jobs_lost / (total_time / 60), 1)

    # compute average wait times per iteration and compute a total average
    avg_time_to_merge = round(statistics.mean(wait_times), 1)

    # compute median of the wait times per iternation
    median_time_to_merge = round(statistics.median(wait_times), 1)
    
    return (throughput, jobs_lost_rate, avg_time_to_merge, median_time_to_merge)


def main():

    # parse the CLI args
    parser = argparse.ArgumentParser(description="Merge queue throughput simulator.")
    parser.add_argument("--job-duration", dest="job_duration", required=True, type=int,
                        help="Job duration in minutes.")
    parser.add_argument("--failure-probability", dest="failure_probability", required=True, type=float,
                        help="Job failure probability expressed as a number between 0 and 1.")
    parser.add_argument("--max-queue-size", dest="max_queue_size", required=False, default=10, type=int,
                        help="Maximum queue size to simulate.")
    parser.add_argument("--min-queue-size", dest="min_queue_size", required=False, default=1, type=int,
                        help="Minimum queue size to simulate.")
    parser.add_argument("--sim-duration", dest="sim_duration", required=False, default=10000, type=int,
                        help="Simulation duration in hours.")
    parser.add_argument("--jobs_waiting_to_enter", dest="jobs_waiting_to_enter", required=False, default=0, type=int,
                        help="Number of jobs waiting to enter the queue simulating a queue being full and jobs waiting.")
    parser.add_argument("--jobs_waiting_to_enter_probability", dest="jobs_waiting_to_enter_probability", required=False, default=0, type=float,
                        help="Probability of jobs waiting to enter the queue.  This setting determines how often there is an occurance of 'jobs_waiting_to_enter' waiting to enter the queue simulating queue being full and jobs waiting.")  
    args = parser.parse_args()

    if args.failure_probability < 0 or args.failure_probability > 1:
        raise ValueError("Failure rate must be a number between 0 and 1.")
    
    if args.jobs_waiting_to_enter_probability < 0 or args.jobs_waiting_to_enter_probability > 1:
        raise ValueError("Jobs waiting to enter probability must be a number between 0 and 1.")
    
    # Define queue sizes to test
    queue_sizes = range(args.min_queue_size, args.max_queue_size+1, 1)

    logger.info("")
    logger.info(f"Job duration : {args.job_duration}m")
    logger.info(f"Job failure probability : {args.failure_probability}")
    logger.info(f"Jobs waiting to enter the queue probability : {args.jobs_waiting_to_enter_probability}")
    logger.info(f"Jobs waiting to enter the queue : {args.jobs_waiting_to_enter}")
    logger.info(f"Simulation duration : {args.sim_duration}h")
    logger.info("")
    logger.info("Q Size | Throughput (PR/h) | Avg Time to Merge (m) | Median Time to Merge (m) | PRs Lost (PR/h)")
    logger.info("-------|-------------------|-----------------------|--------------------------|-----------------")
    # Simulate throughput for each queue size
    for queue_size in queue_sizes:
        throughput, jobs_lost_rate, avg_time_to_merge, median_time_to_merge = \
            simulate_throughput(queue_size,
                                args.sim_duration * 60,
                                args.job_duration,
                                args.failure_probability,
                                jobs_waiting_to_enter=args.jobs_waiting_to_enter,
                                jobs_waiting_to_enter_probability=args.jobs_waiting_to_enter_probability)
        logger.info(f"{queue_size:<6} | {throughput:<17} | {avg_time_to_merge:<21} | {median_time_to_merge:<24} | {jobs_lost_rate}")
    
    logger.info("")


if __name__ == "__main__":
    exit(main())
