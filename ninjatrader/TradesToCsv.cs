#region Using declarations
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.DataAnnotations;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Input;
using System.Windows.Media;
using System.Xml.Serialization;
using NinjaTrader.Cbi;
using NinjaTrader.Gui;
using NinjaTrader.Gui.Chart;
using NinjaTrader.Gui.SuperDom;
using NinjaTrader.Gui.Tools;
using NinjaTrader.Data;
using NinjaTrader.NinjaScript;
using NinjaTrader.Core.FloatingPoint;
using NinjaTrader.NinjaScript.Indicators;
using NinjaTrader.NinjaScript.DrawingTools;
using System.IO;
using System.Runtime.InteropServices;
#endregion
//NOTE: All strategies that you want to track need IncludeTradeHistoryInBacktest= true;

//This namespace holds Strategies in this folder and is required. Do not change it. 
namespace NinjaTrader.NinjaScript.Strategies
{
    public class TradesToCsv : Strategy
    {
        private string fileName;

        protected override void OnStateChange()
        {
            if (State == State.SetDefaults)
            {
            }
            else if (State == State.Configure)
            {
				//G:\My Drive\Coding Projects\Python\PyCharm\StrategyPortfolioAnalyzer\data\in
				// Default to Desktop if nothing entered in Save Directory
				if (saveDir.IsNullOrEmpty())
				{
					//fileName = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Desktop), "todaytrades.csv");
					fileName = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
					Print($"Save Directory is empty defaulting to Desktop: {fileName}");
				}
				else
				{
					//fileName = Path.Combine(saveDir, "todaytrades.csv");
					fileName = saveDir;
					Print($"Save file name set to: {fileName}");
				}
            }
        }

        protected override void OnBarUpdate()
        {
			//if (State == State.Realtime)
            if (State == State.Historical && CurrentBar == 0)
            {
                double tradePnL = 0.00;
				List<StratTrades> strategyList = new List<StratTrades>();
                foreach (Account sampleAccount in Account.All)
                {
                    //{// CHANGE THE ACCOUNT HERE YOU WANT TO TRACK
					// Save Trades from every Account Except Sim101
                    if (sampleAccount.Name != "Sim101")
                    {
                        try
                        {
                            try
                            {
                                foreach (StrategyBase strat in sampleAccount.Strategies)
                                {
                                    if (!strat.IsTerminal)
                                    {
										string stratName;
										int index = strat.DisplayName.IndexOf('(');
										if (index >= 0) stratName = strat.DisplayName.Substring(0, index).Trim();
										else stratName = strat.DisplayName;
										// Create new strategy object for a New Strategy
										var stratTradeObj = new StratTrades(stratName);
                                        foreach (Trade trd in strat.SystemPerformance.AllTrades)
                                        {
											//Only check for yesterday, since this should run after midnight?
											if (trd.Entry.Time.Date == DateTime.Today.Date.AddDays(-1))
											{
												tradePnL += trd.ProfitCurrency;
	                                            Print(strat.Name+","+trd.Entry.Instrument.MasterInstrument.Name+","+trd.Quantity+","+trd.Entry.Order.Name+","+trd.Entry.Time+","+trd.Entry.Price);
												stratTradeObj.tradeList.Add(trd);
											}
                                        }
										// Add Strategy object to our list for writing to csv file at the end
										if (stratTradeObj.tradeList.Count > 0)
											strategyList.Add(stratTradeObj);
                                    }
                                }
								// Only Create todaytrades.csv file if we have trades today
								if (strategyList.Count > 0)
								{
                                	WriteToCSV(fileName, strategyList);
									NinjaScript.Log($"TradesToCsv: PnL: {tradePnL} Saved {strategyList.Count} Stategies to path: {fileName}", LogLevel.Information);
								}
								else
								{
									NinjaScript.Log($"TradesToCsv: No Trades to save to a csv today.", LogLevel.Information);
								}
                            }
                            catch (Exception ex) { NinjaScript.Log($"TradesToCsv: ERROR: {ex.Message}", LogLevel.Error); }
                        }
                        catch (Exception ex) { NinjaScript.Log($"TradesToCsv: ERROR: {ex.Message}", LogLevel.Error); }
                    }
                }

            }
        }
		
		public class StratTrades
	    { // Container Class for holding Strategy Statistics
	        public string stratName { get; set; }
	        public List<Trade> tradeList { get; set; }
	
	        public StratTrades(string name)
	        {
	            stratName = name;
	            tradeList = new List<Trade>();
	        }
	    }


        public void WriteToCSV(string filePath, List<StratTrades> strategyList)
        { // Write to a StratTrades Objects to a CSV
			string currentDate = DateTime.Now.ToString("yyyyMMdd");
			foreach (var strategy in strategyList)
			{
	            var csvBuilder = new StringBuilder();
				csvBuilder.AppendLine("Trade number,Instrument,Account,Strategy,Market pos.,Qty,Entry price,Exit price,Entry time,Exit time,Entry name,Exit name,Profit,Cum. net profit,Commission,MAE,MFE,ETD,Bars,");
	            foreach (var trade in strategy.tradeList)
	            {
	                string marketPos = trade.Entry.MarketPosition == MarketPosition.Long ? "Long" : "Short";
					var row = new string[]
	                {
	            		trade.TradeNumber.ToString(),
						trade.Entry.Instrument.FullName,
						trade.Entry.Account.Name,
						strategy.stratName,
						marketPos,
						trade.Quantity.ToString(),
						trade.Entry.Price.ToString(),
						trade.Exit.Price.ToString(),
			            trade.Entry.Time.ToString("MM/dd/yyyy h:m:s tt"),
			            trade.Exit.Time.ToString("MM/dd/yyyy h:m:s tt"),
						trade.Entry.Name,
						trade.Exit.Name,
			            trade.ProfitCurrency.ToString(),
						"0.00", //I will not get a correct answer here anyway
						trade.Commission.ToString(),
						trade.MaeCurrency.ToString(),
						trade.MfeCurrency.ToString(),
						Math.Round(trade.TotalEfficiency, 2).ToString(),
						"0", // Bars is 0 for now
	                };
	
	                csvBuilder.AppendLine(string.Join(",", row.Select(value => "" + value + "")) + ","); // Adding quotes to each value to handle commas within values
	            }
				
				string csvFileName = Path.Combine(filePath, $"{currentDate}-{strategy.stratName}.csv");
	            // Write to file
	            File.WriteAllText(csvFileName, csvBuilder.ToString());
			}
        }

		#region Properties
		[NinjaScriptProperty]
		[Display(Name="Save Directory", Description="Directory to save csv file to", Order=1, GroupName="Parameters")]
		public string saveDir
		{ get; set; }
		#endregion
    }
}

