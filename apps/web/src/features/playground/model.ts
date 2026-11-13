export const MODEL_VERSION = "0.3.0";
export const INITIAL_RESERVE_X = 10_000;
export const INITIAL_RESERVE_Y = 10_000;
export const INITIAL_CEX_PRICE = 1;
export const SUSTAINED_BAND_TICKS = 2;

export type TrackingParameters = {
  shockLogReturn: number;
  shockTick: number;
  horizonTicks: number;
  executionDelayTicks: number;
  noArbitrageBandLog: number;
  capacityFraction: number;
};

export type TrackingPoint = {
  tick: number;
  cexPrice: number;
  dexPrice: number;
  logError: number;
  excessError: number;
};

export type TrackingResult = {
  points: TrackingPoint[];
  maxAbsoluteLogError: number;
  maxExcessError: number;
  sustainedReturnTick: number | null;
};

type Order = { side: "sell-x" | "buy-x"; amount: number };

const price = (reserveX: number, reserveY: number) => reserveY / reserveX;
const logError = (reserveX: number, reserveY: number, reference: number) =>
  Math.log(price(reserveX, reserveY) / reference);

function swapXForY(reserveX: number, reserveY: number, amountX: number): [number, number] {
  const amountOutY = (reserveY * amountX) / (reserveX + amountX);
  return [reserveX + amountX, reserveY - amountOutY];
}

function swapYForX(reserveX: number, reserveY: number, amountY: number): [number, number] {
  const amountOutX = (reserveX * amountY) / (reserveY + amountY);
  return [reserveX - amountOutX, reserveY + amountY];
}

function arbitrageOrder(
  reserveX: number,
  reserveY: number,
  reference: number,
  band: number,
  capacity: number
): Order | null {
  const error = logError(reserveX, reserveY, reference);
  if (Math.abs(error) <= band + 1e-12 || capacity <= 0) return null;

  const invariant = reserveX * reserveY;
  if (error > band) {
    const targetPrice = reference * Math.exp(band);
    const neededX = Math.max(Math.sqrt(invariant / targetPrice) - reserveX, 0);
    const amountX = Math.min(neededX, capacity * reserveX);
    return amountX > 0 ? { side: "sell-x", amount: amountX } : null;
  }

  const targetPrice = reference * Math.exp(-band);
  const neededY = Math.max(Math.sqrt(invariant * targetPrice) - reserveY, 0);
  const amountY = Math.min(neededY, capacity * reserveY);
  return amountY > 0 ? { side: "buy-x", amount: amountY } : null;
}

function executeOrder(reserveX: number, reserveY: number, order: Order): [number, number] {
  return order.side === "sell-x"
    ? swapXForY(reserveX, reserveY, order.amount)
    : swapYForX(reserveX, reserveY, order.amount);
}

export function runTracking(parameters: TrackingParameters): TrackingResult {
  let reserveX = INITIAL_RESERVE_X;
  let reserveY = INITIAL_RESERVE_Y;
  let reference = INITIAL_CEX_PRICE;
  let pendingOrder: Order | null = null;
  let pendingExecuteTick: number | null = null;
  let inBandStreak = 0;
  let sustainedReturnTick: number | null = null;
  const points: TrackingPoint[] = [];
  const record = (tick: number) => {
    const error = logError(reserveX, reserveY, reference);
    points.push({
      tick,
      cexPrice: reference,
      dexPrice: price(reserveX, reserveY),
      logError: error,
      excessError: Math.sign(error) * Math.max(Math.abs(error) - parameters.noArbitrageBandLog, 0)
    });
  };

  record(0);
  for (let tick = 1; tick <= parameters.horizonTicks; tick += 1) {
    if (tick === parameters.shockTick) {
      reference *= Math.exp(parameters.shockLogReturn);
    }

    let executedDelayedOrder = false;
    if (pendingOrder && pendingExecuteTick !== null && tick >= pendingExecuteTick) {
      [reserveX, reserveY] = executeOrder(reserveX, reserveY, pendingOrder);
      pendingOrder = null;
      pendingExecuteTick = null;
      executedDelayedOrder = true;
    }

    if (!pendingOrder && !executedDelayedOrder) {
      const order = arbitrageOrder(
        reserveX,
        reserveY,
        reference,
        parameters.noArbitrageBandLog,
        parameters.capacityFraction
      );
      if (order && parameters.executionDelayTicks === 0) {
        [reserveX, reserveY] = executeOrder(reserveX, reserveY, order);
      } else if (order) {
        pendingOrder = order;
        pendingExecuteTick = tick + parameters.executionDelayTicks;
      }
    }

    record(tick);
    const error = Math.abs(points[points.length - 1].logError);
    if (error <= parameters.noArbitrageBandLog + 1e-12) {
      inBandStreak += 1;
      if (sustainedReturnTick === null && inBandStreak >= SUSTAINED_BAND_TICKS) {
        sustainedReturnTick = tick - SUSTAINED_BAND_TICKS + 1;
      }
    } else {
      inBandStreak = 0;
    }
  }

  return {
    points,
    maxAbsoluteLogError: Math.max(...points.map((point) => Math.abs(point.logError))),
    maxExcessError: Math.max(...points.map((point) => Math.max(Math.abs(point.logError) - parameters.noArbitrageBandLog, 0))),
    sustainedReturnTick
  };
}

export type FixedSaleResult = {
  remainingReserveFraction: number;
  reserveXBeforeSale: number;
  reserveYBeforeSale: number;
  reserveXAfterSale: number;
  reserveYAfterSale: number;
  absoluteLogPriceImpact: number;
  percentagePriceChange: number;
};

export function runFixedSale(fixedSaleX: number, remainingReserveFraction: number): FixedSaleResult {
  const reserveXBeforeSale = INITIAL_RESERVE_X * remainingReserveFraction;
  const reserveYBeforeSale = INITIAL_RESERVE_Y * remainingReserveFraction;
  const [reserveXAfterSale, reserveYAfterSale] = swapXForY(
    reserveXBeforeSale,
    reserveYBeforeSale,
    fixedSaleX
  );
  const priceBefore = price(reserveXBeforeSale, reserveYBeforeSale);
  const priceAfter = price(reserveXAfterSale, reserveYAfterSale);

  return {
    remainingReserveFraction,
    reserveXBeforeSale,
    reserveYBeforeSale,
    reserveXAfterSale,
    reserveYAfterSale,
    absoluteLogPriceImpact: Math.abs(Math.log(priceAfter / priceBefore)),
    percentagePriceChange: priceAfter / priceBefore - 1
  };
}
