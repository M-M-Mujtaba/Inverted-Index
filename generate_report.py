from json import load
import matplotlib.pyplot as plt

def Generate_Table(report, report_data):
    report.write("##Report Table \n\n")
    report.write("| Query ID |")
    for p in report_data.keys():
        report.write(f" P{p} |  |")
    report.write("\n")
    report.write("| :---: |")
    for p in report_data.keys():
        report.write(" ---: | :--- |")

    report.write("\n")
    report.write("| |")
    for p in report_data.keys():
        report.write(" Okapi-TF| Vector-Score|")
    report.write("\n")

    for query_id in report_data['1']["Okapi TF"].keys():

        report.write(f"| {query_id} |")
        for p in report_data.keys():
            report.write(f" {'{:.3f}'.format(report_data[p]['Okapi TF'][query_id])} |")
            report.write(f" {'{:.3f}'.format(report_data[p]['Vector Space'][query_id])} |")
        report.write('\n')
    report.write('\n\n')
def save_plot(report_data, name):
    Ps = [int(P) for P in report_data.keys()]
    print(Ps)
    okapi_avg = [data["Okapi TF"]["Average NDCG"] for data in report_data.values()]
    vector_score_avg = [data["Vector Space"]["Average NDCG"] for data in report_data.values()]
    print(okapi_avg)

    fig = plt.figure()
    plt.plot(Ps, okapi_avg, 'r', label='Okapi TF')
    plt.plot(Ps, vector_score_avg, 'b', label='Vector Space')
    plt.ylabel("Avg NDCG")
    plt.xlabel("P")
    plt.legend()
    fig.savefig(name)

if __name__ == "__main__":

    with open("report_data.json") as report_data_file:
        report_data = load(report_data_file)


    with open("report.md", "w") as report:
        report.write("#NDCG REPORT \n")
        Generate_Table(report, report_data)

        plot_name = "p_graph.png"
        save_plot(report_data, plot_name)
        report.write("##Average NDCG Okapi-TF vs Vector Space plot for P values \n")

        report.write(f'![Graph]({plot_name})')
        report.write("\n As observed from the Graph Vector Space outperforms Okapi ")


