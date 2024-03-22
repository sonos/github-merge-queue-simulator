#!/usr/bin/env python3

import random
import logging
import argparse
import statistics

logging.basicConfig(level=logging.INFO, format='  %(message)s')
logger = logging.getLogger(__name__)


def simulate_throughput(queue_size: int, sim_duration: int, job_duration: int, failure_rate: float) -> float:
    """Compute the throughput of a queue given the queue size, duration, and failure rate.
    
    Args:
        queue_size (int): Number of jobs in the queue
        sim_duration (int): Duration of the simulation in minutes
        job_duration (int): Duration of each job in minutes
        failure_rate (float): Probability of a job failing expressed as a number between 0 and 1

    Returns:
        tuple: a tuple containing throughput of jobs per hour, average time to merge in minutes, and median time to merge in minutes
    """
    total_jobs_completed = 0
    total_time = 0
    
    # track a list of all wait times per iteration
    wait_times = []

    # run simulation
    while total_time < sim_duration:
        
        jobs_completed = 0

        # roll through the queue and pick a job to fail based on probability
        for _ in range(1, queue_size + 1):
            # if job failure occurs based on probability
            if random.random() < failure_rate:
                break
            
            # job completed OK
            else:
                jobs_completed += 1
        
        # track jobs completed in this iteration
        total_jobs_completed += jobs_completed
        
        # increment by job execution time
        total_time += job_duration

        # can't divide by zero, this happens if the first jobs gets bounced and displaces all jobs, ignore that case
        if jobs_completed > 0:
            # wait time is: jobs / rate of jobs completing
            # from Little's Law: https://en.wikipedia.org/wiki/Little%27s_law
            wait_times.append(queue_size / (jobs_completed / job_duration))


    # compute throughput of jobs / hour, 1 decimal point
    throughput = round(total_jobs_completed / (total_time / 60), 1)

    # compute average wait times per iteration and compute a total average
    avg_time_to_merge = round(statistics.mean(wait_times), 1)

    # compute median of the wait times per iternation
    median_time_to_merge = round(statistics.median(wait_times), 1)
    
    return (throughput, avg_time_to_merge, median_time_to_merge)


def main():

    # parse the CLI args
    parser = argparse.ArgumentParser(description="Merge queue throughput simulator.")
    parser.add_argument("--max-queue-size", dest="max_queue_size", required=False, default=10, type=int, help="Maximum queue size to simulate.")
    parser.add_argument("--min-queue-size", dest="min_queue_size", required=False, default=1, type=int, help="Minimum queue size to simulate.")
    parser.add_argument("--sim-duration", "-s", dest="sim_duration", required=False, default=96, type=int, help="Simulation duration in hours.")
    parser.add_argument("--job-duration", "-j", dest="job_duration", required=True, type=int, help="Job duration in minutes.")
    parser.add_argument("--failure-rate", "-f", dest="failure_rate", required=True, type=float, help="Failure rate expressed as a number between 0 and 1.")
    args = parser.parse_args()

    if args.failure_rate < 0 or args.failure_rate > 1:
        raise ValueError("Failure rate must be a number between 0 and 1.")
    
    # Define queue sizes to test
    queue_sizes = range(args.min_queue_size, args.max_queue_size+1, 1)

    logger.info("")
    logger.info(f"Simulation duration: {args.sim_duration}h")
    logger.info(f"Job duration: {args.job_duration}m")
    logger.info(f"Failure rate: {args.failure_rate}")
    logger.info("")
    logger.info("Q Size | Throughput (PR/h) | Avg Time to Merge (m) | Median Time to Merge (m)")
    logger.info("-------|-------------------|-----------------------|-------------------------")
    # Simulate throughput for each queue size
    for queue_size in queue_sizes:
        throughput, avg_time_to_merge, median_time_to_merge = \
            simulate_throughput(queue_size,
                                args.sim_duration * 60,
                                args.job_duration,
                                args.failure_rate)
        logger.info(f"{queue_size:<6} | {throughput:<17} | {avg_time_to_merge:<21} | {median_time_to_merge:<23}")
    
    logger.info("")


if __name__ == "__main__":
    exit(main())
