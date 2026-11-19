"""apply_pack.py <tree>: rewrite the listed example-mini rows in place (only the text column and updated_by), keeping
every other line byte-identical."""
import csv, io, sys
TAG = "w6-fix-length proposal"
MP = {  # mark_points.csv: id -> point
 "ped_definition_p2": "PED has no units, so it compares goods with different prices",
 "ped_definition_p3": "A price rise cuts the quantity demanded, so the value of PED is negative",
 "ped_formula_p1": "Each % change is the change divided by the original value, times 100",
 "tax_supply_shift_p1": "The tax raises firms' costs, so the supply curve shifts up by the tax per unit",
 "tax_incidence_split_p2": "When demand is price elastic, producers bear more of the tax",
}
MC = {  # misconceptions.csv: id -> wrong_idea
 "ped_definition_m1": "The slope of the demand curve is PED, so it is the same all along it",
 "ped_definition_m2": "PED measures how far the price changes when the demand changes",
 "ped_formula_m1": "Divide the change in price by the change in quantity demanded to get PED",
 "ped_formula_m2": "Work out each percentage change using the new value, not the original",
 "ped_formula_m3": "PED is the change in quantity over the change in price, with no percentages",
 "ped_values_m1": "An elastic good has a PED below 1, since demand for it hardly changes",
 "pes_definition_m1": "Supply is just as price elastic in the short run as in the long run",
 "pes_definition_m2": "If buyers have lots of substitutes to switch to, supply is price elastic",
 "pes_formula_m1": "PES is usually negative, just as PED is for most goods we buy",
 "pes_formula_m2": "PES divides the % change in price by the % change in quantity supplied",
 "yed_definition_m1": "YED measures how demand responds to a change in its own price",
 "tax_supply_shift_m1": "Because buyers now pay more, an indirect tax shifts the demand curve left",
 "tax_supply_shift_m2": "An ad valorem tax shifts the supply curve by the same amount at every price",
 "tax_incidence_split_m1": "Producers bear the tax, as they hand the money to the government",
 "tax_incidence_split_m2": "If demand is price inelastic, producers bear most of the tax burden",
 "externality_tax_eval_m1": "A pollution tax at the right level brings pollution down to zero",
 "externality_tax_eval_m2": "Firms just pay a pollution tax and carry on, so output doesn't change",
}
def rewrite(path, col, new):
    raw = open(path, newline="").read().split("\n")
    header = next(csv.reader([raw[0]]))
    out, done = [], set()
    for line in raw:
        row = next(csv.reader([line])) if line else []
        if row and row[0] in new:
            row[header.index(col)] = new[row[0]]
            row[header.index("updated_by")] = TAG
            buf = io.StringIO(); csv.writer(buf, lineterminator="").writerow(row); line = buf.getvalue(); done.add(row[0])
        out.append(line)
    assert done == set(new), set(new) - done
    open(path, "w", newline="").write("\n".join(out))
t = sys.argv[1] + "/coursepacks/example-mini/"
rewrite(t + "mark_points.csv", "point", MP)
rewrite(t + "misconceptions.csv", "wrong_idea", MC)
