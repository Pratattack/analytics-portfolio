from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from model import bill,twelve_cycles

ROOT=Path(__file__).resolve().parents[1]
def make_charts(plans,profiles):
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.facecolor':'#101b2a','figure.facecolor':'#101b2a','text.color':'#ecf2fa','axes.labelcolor':'#c9d9ea','xtick.color':'#c9d9ea','ytick.color':'#c9d9ea','axes.edgecolor':'#617087','savefig.facecolor':'#101b2a'})
    basic=next(p for p in plans if p['id']=='discount-basic-36');credit=next(p for p in plans if p['id']=='discount-credit-12')
    fig,ax=plt.subplots(figsize=(10,5.6),layout='constrained')
    for p,color in [(basic,'#65c9ff'),(credit,'#ffd38b')]:
        # Separate segments avoid drawing a nonexistent continuous transition.
        for a,b in ([(250,999),(1000,3000)] if p['credit_rule']=='gte' else [(250,3000)]):
            x=list(range(a,b+1));ax.plot(x,[bill(p,q,normalized=True)['total'] for q in x],color=color,lw=2.5,label=p['name'] if a==250 else None)
    ax.scatter([999,1000],[bill(credit,q,normalized=True)['total'] for q in [999,1000]],color='#ffd38b',s=35,zorder=5)
    ax.axvline(1000,color='#b9c8da',ls=':',alpha=.6)
    ax.annotate('Credit begins at 1,000 kWh\n$125 threshold credit',xy=(1000,bill(credit,1000,normalized=True)['total']),xytext=(1350,100),arrowprops={'arrowstyle':'->','color':'#ecf2fa'},color='#ecf2fa')
    ax.set(title='A lower-use month can cost more',xlabel='Electricity per billing cycle (kWh)',ylabel='Modeled recurring bill ($, before taxes)');ax.grid(alpha=.13);ax.legend(facecolor='#101b2a',labelcolor='#ecf2fa',loc='upper left')
    fig.get_layout_engine().set(rect=(0,.07,1,.93))
    fig.text(.13,.015,'Contract-derived curves. October delivery charges held constant. Not observed bills or enrollment quotes.',fontsize=8,color='#c9d9ea')
    for ext in ['png','svg']:fig.savefig(ROOT/f'results/threshold_curve.{ext}',dpi=160,bbox_inches='tight')
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(11,5.4),layout='constrained')
    axes[0].plot(range(1,13),profiles[0]['usage'],color='#65c9ff',lw=2,label='Steady usage');axes[0].plot(range(1,13),profiles[1]['usage'],color='#ffd38b',marker='o',label='Uneven usage');axes[0].axhline(1000,ls=':',color='#c9d9ea',alpha=.6)
    axes[0].set(xlabel='Billing cycle (30 days each)',ylabel='Usage (kWh)',title='Same total: 12,000 kWh');axes[0].legend(facecolor='#101b2a',labelcolor='#ecf2fa',fontsize=9);axes[0].grid(alpha=.13)
    values=[twelve_cycles(credit,p['usage'])['total'] for p in profiles[:2]]
    axes[1].bar(['Steady','Uneven'],values,color=['#65c9ff','#ffd38b'],width=.55)
    for i,v in enumerate(values):axes[1].text(i,v+20,f'${v:,.2f}',ha='center')
    axes[1].set(ylabel='Modeled total ($, before taxes)',title='Same contract, $750 difference',ylim=(0,max(values)*1.2));axes[1].grid(axis='y',alpha=.13)
    fig.get_layout_engine().set(rect=(0,.08,1,.92))
    fig.text(.08,.015,'Hypothetical usage profiles. Discount Power Bill Credit Bundle 12. Fixed October delivery charges; no renewal.',fontsize=8,color='#c9d9ea')
    for ext in ['png','svg']:fig.savefig(ROOT/f'results/equal_total_scenario.{ext}',dpi=160,bbox_inches='tight')
    plt.close(fig)
