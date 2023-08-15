import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("TKAgg")
import readTDR

# colors
hit_prfix_col = [1, 0.65, 0.65]
hituehit_col = [0, 0, 0]
hit_col = "r"
e_hit_col = [1, 0.7, 0]
wr_hit_col = [0.6, 0, 0.6]
e_wr_hit_col = [0.86, 0.39, 0.86]
early_col = "g"
late_col = "b"
eye_col = [0.5, 0.5, 0.5]
catch_col = [0.75, 0.75, 0]

if __name__ == "__main__":
    filename = "test.tdr"
    headers: list[readTDR.Header] = readTDR.read_tdr(filename)
    trials: list[readTDR.TrialHeader] = [
        header for header in headers if header.id == "$TH1"
    ]
    hits = [header for header in trials if header.outcome == readTDR.TrialOutcome.Hit]
    # time_vec = tdr.trialtime/60;
    # tm_win = [0; time_vec(end)];

    # hituehit= find(tdr.result == 1 | tdr.result == 3);%hit + ehit zusammen
    # hit     = find(tdr.result == 1);
    # wro     = find(tdr.result == 2);
    # e_hit   = find(tdr.result == 3);
    # ewro    = find(tdr.result == 4);
    # early   = find(tdr.result == 5);
    # late    = find(tdr.result == 6);
    # eyeerr  = find(tdr.result == 7);
    # nost    = find(tdr.result == 0);
    # all_ev  = [hit; e_hit; wro; ewro; early; late; eyeerr];
    # wrk_ev  = [hit; e_hit; wro; ewro; early; late];
    # wrk_wro  = [hit; e_hit; wro; ewro];

    plt.Figure()
    plt.subplot(position=[0.046, 0.695, 0.951, 0.2975])

    x = [trial.subheader1.tRelTrialStartMIN for trial in hits]
    y = [trial.reactionTimeMS for trial in hits]
    # plot hits
    plt.plot(
        x,
        y,
        "s",
        markeredgecolor=hit_col,
        markerfacecolor=hit_col,
        markersize=2,
    )

    # subplot('Position',[0.046 0.695 0.951 0.2975]);%%[0.035 0.695 0.96 0.2975]
    # hold on;

    # plot(time_vec(late) ,trialtime(late)   ,'s', 'MarkerEdgeColor', late_col,    'MarkerFaceColor', late_col,'MarkerSize',2);
    # plot(time_vec(early),trialtime(early)  ,'s', 'MarkerEdgeColor', early_col,   'MarkerFaceColor', early_col, 'MarkerSize',2);
    # plot(time_vec(hituehit)  ,trialtime(hituehit)    ,'s', 'MarkerEdgeColor', hituehit_col,     'MarkerFaceColor', hituehit_col,'MarkerSize',2);
    # plot(time_vec(hit)  ,trialtime(hit)    ,'s', 'MarkerEdgeColor', hit_prfix_col,     'MarkerFaceColor', hit_col,'MarkerSize',2);
    # plot(time_vec(e_hit),trialtime(e_hit)  ,'s', 'MarkerEdgeColor', e_hit_col,   'MarkerFaceColor', e_hit_col,'MarkerSize',2);
    # plot(time_vec(wro)  ,trialtime(wro)    ,'s', 'MarkerEdgeColor', wr_hit_col,  'MarkerFaceColor', wr_hit_col,'MarkerSize',2);
    # plot(time_vec(ewro) ,trialtime(ewro)   ,'s', 'MarkerEdgeColor', e_wr_hit_col,'MarkerFaceColor', e_wr_hit_col,'MarkerSize',2);
    # plot(time_vec(eyeerr),trialtime(eyeerr),'s', 'MarkerEdgeColor', eye_col,     'MarkerFaceColor', eye_col, 'MarkerSize',2);

    # plot(time_vec(fixi)  ,trialtime(fixi)    ,'s', 'MarkerEdgeColor', hit_col,   'MarkerFaceColor', hit_prfix_col,'MarkerSize',2);
    # plot(time_vec(nost)  ,trialtime(nost)    ,'s', 'MarkerEdgeColor', catch_col,   'MarkerFaceColor', catch_col,'MarkerSize',2);

    # %set(gca,'Color',[0 0 0]);
    # %set(gca,'XColor',[0.8 0.9 0.6]);
    # %set(gca,'YColor',[0.8 0.9 0.6]);
    # set(gca,'TickDir','out');
    # xlim(tm_win);
    # box on;
    # ylabel('bar release time [s]');
    # plot(tm_win,[0,0],'Color',[0 0 0],'LineWidth',1);%plot(tm_win,[0,0],'Color',[0.8 0.9 0.6],'LineWidth',1);
    # create random data
    # no_of_balls = 25
    # x = [random.triangular() for i in range(no_of_balls)]
    # y = [random.gauss(0.5, 0.25) for i in range(no_of_balls)]
    # colors = [random.randint(1, 4) for i in range(no_of_balls)]
    # areas = [math.pi * random.randint(5, 15) ** 2 for i in range(no_of_balls)]
    # # draw the plot
    # # plt.figure()
    # plt.scatter(x, y, s=areas, c=colors, alpha=0.85)
    # # plt.axis([0.0, 1.0, 0.0, 1.0])
    # plt.xlabel("X")
    # plt.ylabel("Y")
    plt.show()
