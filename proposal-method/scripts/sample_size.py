#!/usr/bin/env python3
"""Approximate SRS proportion precision or equal independent two-proportion size.
No clinical assumptions are selected. Python standard library only.
"""
import argparse
import json
import math
from statistics import NormalDist


def probability(value):
    number = float(value)
    if not math.isfinite(number) or not 0 < number < 1:
        raise argparse.ArgumentTypeError('must be finite and strictly between 0 and 1')
    return number


def loss_fraction(value):
    number = float(value)
    if not math.isfinite(number) or not 0 <= number < 1:
        raise argparse.ArgumentTypeError('must be finite and in [0, 1)')
    return number


def population_size(value):
    number = int(value)
    if number < 2:
        raise argparse.ArgumentTypeError('population must be an integer of at least 2')
    return number


def calculate(args):
    normal = NormalDist()
    za = normal.inv_cdf(1 - args.alpha / 2)
    if args.mode == 'prevalence':
        raw_infinite = za ** 2 * args.p * (1 - args.p) / args.precision ** 2
        raw = (raw_infinite / (1 + (raw_infinite - 1) / args.population)
               if args.population else raw_infinite)
        raw = max(1.0, raw)
        groups = 1
        method = 'Wald normal approximation for SRS absolute proportion precision'
        if args.population:
            method += '; finite population without replacement correction'
    else:
        if args.p1 == args.p2:
            raise ValueError('p1 and p2 must differ')
        if args.power <= 0.5:
            raise ValueError('this approximation requires power greater than 0.5')
        pb = (args.p1 + args.p2) / 2
        zb = normal.inv_cdf(args.power)
        raw = ((za * math.sqrt(2 * pb * (1-pb)) + zb * math.sqrt(
            args.p1 * (1-args.p1) + args.p2 * (1-args.p2))) ** 2 / (args.p1-args.p2) ** 2)
        groups = 2
        method = 'Two-sided pooled-null/unpooled-alternative normal approximation; equal independent groups; no continuity correction'
    if not math.isfinite(raw):
        raise ValueError('nonfinite sample size; inspect input precision or effect size')
    required = math.ceil(raw)
    recruit = math.ceil(required / (1-args.loss))
    result = {
        'method': method,
        'inputs': vars(args),
        'raw_required_per_group': raw,
        'required_per_group': required,
        'recruit_per_group': recruit,
        'groups': groups,
        'total_required': required * groups,
        'total_recruit': recruit * groups,
        'rounding': 'ceil raw requirement, divide integer requirement by retention, ceil again',
        'limitations': ['Approximation only; no guarantee of power in sparse data or complex designs.',
                        'No cluster, unequal-allocation, paired, survival, or noninferiority calculation.'],
    }
    if args.mode == 'prevalence':
        result['raw_infinite_population'] = raw_infinite
        if args.population and recruit > args.population:
            result['limitations'].append('Recruitment target exceeds the finite population; revise feasibility or precision.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='mode', required=True)
    prevalence = sub.add_parser('prevalence')
    prevalence.add_argument('--p', type=probability, required=True)
    prevalence.add_argument('--precision', type=probability, required=True)
    prevalence.add_argument('--population', type=population_size)
    two = sub.add_parser('two-proportions')
    two.add_argument('--p1', type=probability, required=True)
    two.add_argument('--p2', type=probability, required=True)
    two.add_argument('--power', type=probability, required=True)
    for command in (prevalence, two):
        command.add_argument('--alpha', type=probability, required=True)
        command.add_argument('--loss', type=loss_fraction, default=0)
    args = parser.parse_args()
    try:
        result = calculate(args)
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
